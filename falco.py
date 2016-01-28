#!/usr/bin/python3
import glob, os, socket, time, re, string, sys, json
import threading
import queue as Queue
from ssl import wrap_socket
from log import log
import utils
import imp
from multiprocessing import Process
import websocket
import random, shelve, base64

global reload_plugins
global config_file, conf

def reload_handlers(init=False):
    handlers = set(glob.glob(os.path.join("handles", "*.py")))
    for filename in handlers:
        mtime = os.stat(filename).st_mtime
        if mtime != mtimes.get(filename):
            mtimes[filename] = mtime
            try:
                eval(compile(open(filename, 'U').read(), filename, 'exec'), globals())
            except Exception as e:
                log.critical("Unable to reload %s: %s", filename, e)
                if init:
                    sys.exit(1)
                continue
            log.info("(Re)Loaded %s", filename)

def reload_plugins(init=False):
    plugins_folder = [os.path.join(os.getcwd(), 'plugins')]
    plugins = set(glob.glob(os.path.join("plugins", "*.py")))
    for plugin in plugins:
        _plugin = os.path.join(os.getcwd(), plugin)
        mtime = os.stat(_plugin).st_mtime
        if mtime != mtimes.get(_plugin):
            mtimes[_plugin] = mtime
            try:
                moduleinfo = imp.find_module(plugin.split("/")[1].split(".")[0], plugins_folder)
                pl = imp.load_source(plugin, moduleinfo[1])
            except ImportError as e:
                if str(e).startswith('No module named'):
                    log.error('Failed to load plugin %r: the plugin could not be found.', plugin)
                else:
                    log.error('Failed to load plugin %r: import error %s', plugin, str(e))
                    if init:
                        sys.exit(1)
            except BaseException as e:
                log.error(e)
                pass
            else:
                if hasattr(pl, 'main'):
                    for server in utils.connections.values():
                        pl.main(server)
                        log.debug('%r Calling main() function of plugin %r', server.netname, pl)
            log.info("(Re)Loaded %s", _plugin)

def reload_config(irc):
    if irc.conf_mtime != os.stat(config_file).st_mtime:
        with open(config_file, "r") as f:
            conf = json.load(f)
        irc.conf_mtime = os.stat(config_file).st_mtime
        irc.conf = conf
        irc.reloadConfig()
        log.debug("(%s) Reloaded config", irc.netname)

def connectall():
    for server in utils.connections.values():
        server.start()

log.info("Starting falco")

mtimes = dict()

class IRC(threading.Thread):

    def __init__(self, conf):
        threading.Thread.__init__(self)
        self.setDaemon                          = True
        self.conf                               = conf
        self.conf_mtime                         = os.stat(config_file).st_mtime
        self.netname                            = self.conf["netname"]
        self.rx                                 = 0
        self.tx                                 = 0
        self.txmsgs                             = 0
        self.rxmsgs                             = 0
        self.started                            = 0
        self.server                             = self.conf["server"]
        self.port                               = self.conf["port"]
        self.ssl                                = self.conf["ssl"]
        self.pingfreq                           = 30
        self.pingtimeout                        = 60
        self.pingwarn                           = 5
        self.password                           = "6675636b796f75"
        self.prefixmodes                        = {'q': '~', 'a': '&', 'v': '+', 'o': '@', 'h': '%'}
        self.connected                          = False
        self.chanmodes                          = {}
        self.modes                              = []
        self.channels                           = {}
        self.nicks                              = {}
        self.hasink                             = True
        self.color                              = 14
        self.buffermaxlen                       = 16003
        self.admins                             = self.conf["admins"]
        self.nicks                              = {}
        self.channels                           = {}
        #self.shelve                             = shelve.open("falco-{}.db".format(self.netname), writeback=True)
        #self.admins = self.conf["admins"]
        #try: self.nicks = self.shelve["nicks"]
        #except: self.nicks = {}
        #try: self.channels = self.shelve["channels"]
        #except: self.channels = {}

        self.title_snarfer_allowed              = []
        self.title_snarfer_ignored_urls         = []

        self.repls                              = None

        self.pingTimer                          = None
        self.pingtime                           = time.time()
        self.lastping                           = self.pingtime
        self.reloadConfig()
        #if self.conf["active"]:
        #    self.run()

    def reloadConfig(self):

        self.reply                              = self.conf["reply"]
        self.nick                               = self.conf["nick"]
        self.user                               = self.conf["ident"]
        self.gecos                              = self.conf["gecos"]
        self.setmodes                           = self.conf["modes"]
        self.prefix                             = self.conf["prefix"]
        self.admins                             = self.conf["admins"]
        self.autojoin                           = self.conf["autojoin"]
        self.ignored                            = self.conf["ignored"]
        self.filter                             = self.conf["filter"]
        self.autokick                           = self.conf["autokick"]
        self.ops                                = self.conf.get("ops", [])

    def run(self):
        

        self.connect()

        while self.connected:
            try:
                data = utils.decode(self.socket.recv(2048))
                self.ibuffer += data
                while "\r\n" in self.ibuffer:
                    reload_handlers()
                    reload_plugins()
                    reload_config(self)

                    line, self.ibuffer = self.ibuffer.split("\r\n", 1)
                    line = line.strip()
                    log.debug("(%s) -> %s", self.netname, line)
                    self.rx += len(line)
                    self.rxmsgs += 1

                    args = line.split(" ")

                    if not args:
                        return

                    elif args[0].startswith(":NickServ!") and "identify" in args:
                        self.send("PRIVMSG NickServ :IDENTIFY {}".format(self.conf["nickserv_password"]))
                        time.sleep(3)

                    elif args[0].startswith(":NickServ!") and "identified" in args:
                        # [':NickServ!NickServ@services.', 'NOTICE', 'falco', ':You', 'are', 'now', 'identified', 'for', '\x02falco\x02.']
                        for chan in self.autojoin:
                            self.send("JOIN {}".format(chan))

                    elif args[0] == "ERROR":
                        # ['ERROR', ':Closing', 'Link:', 'falco[meetmehereonirclo.lol]', '(Excess', 'Flood)']
                        if args[4] == "(Excess" and args[5] == "Flood)":
                            self.reconnect()

                    elif args[0] == "PING":
                        # ['PING', ':blah']
                        #self.send("LUSERS")
                        self.send("PONG {}".format(args[1]))

                    elif args[0] == "AUTHENTICATE":
                        func = globals()["handle_AUTHENTICATE"]
                        func(self, user, args)

                    if args[1] == "PONG":
                        self.pingtime = int(time.time() - self.lastping)
                        self.lastping = time.time()

                        if self.pingtime - self.pingfreq > self.pingwarn:
                            log.warn("(%s) Lag: %s seconds", self.netname,
                                        round(self.pingtime - self.pingfreq, 3))

                        if self.pingtime - self.pingfreq > self.pingtimeout:
                            self.disconnect("Ping timeout: {} seconds".format(
                                    round(self.pingtime - self.pingfreq)), terminate=False)
                            self.connect()

                    try:
                        real_args = []
                        for arg in args:
                            real_args.append(arg)
                            if arg.startswith(':') and args.index(arg) != 0:
                                index = args.index(arg)
                                arg = args[index:]
                                arg = ' '.join(arg)[1:]
                                real_args = args[:index]
                                real_args.append(arg)
                                break

                        real_args[0] = real_args[0].split(':', 1)[1]
                        args = real_args

                        user = args[0]
                        command = args[1]
                        args = args[2:]

                        try:
                            func = globals()['handle_'+command]
                        except KeyError as e:
                            pass
                        else:
                            func(self, user, args)

                    except IndexError:
                        continue

            except KeyboardInterrupt:
                #self.shelve.close()
                self.disconnect("CTRL-C at console.")

    def msg(self, target, message, reply=None):
        reply = self.reply if not reply else reply
        message = message.replace("http", "ht\x0ftp")
        for filter in self.filter:
            message = re.sub(filter, "", message, flags=re.IGNORECASE)
        if self.hasink:
            self.send("{} {} :\x03{}│\x0f {}".format(reply, target, self.color, message))
        else:
            self.send("{} {} :{}".format(reply, target, message))
        time.sleep(0.75)

    def kick(self, chan, target, message="Goodbye"):
        self.send("KICK {} {} :{}".format(chan, target, message))

    #def join(self, chan):
    #    self.send("JOIN {}".format(chan))

    def send(self, data):
        data = data.replace('\n', ' ').replace("\a", "")
        data = data.encode("utf-8") + b"\n"
        stripped_data = data.decode("utf-8").strip("\n")
        if "PASS " not in stripped_data: # don't print PASS output
            log.debug("(%s) <- %s", self.netname, stripped_data)
        self.tx += len(data)
        self.txmsgs += 1
        try:
            self.socket.send(data)
        except AttributeError:
            log.debug("(%s) Dropping message %r; network isn't connected!", self.netname, stripped_data)

    def schedulePing(self):
        #self.shelve["nicks"] = self.nicks
        #self.shelve["channels"] = self.channels
        #self.shelve.sync() # BUG: this ends up creating very large files for some reason
        #                   # 5.9G Jan 11 18:05 falco-freenode.db
        self.send("PING {}".format(time.time()))
        self.pingTimer = threading.Timer(self.pingfreq, self.schedulePing)
        self.pingTimer.daemon = True
        self.pingTimer.start()

    def connect(self):
        self.started = time.time()
        log.debug("(%s) Attempting to connect to %s/%s as %s",
                  self.netname, self.server, self.port, self.nick)
        self.socket = socket.create_connection((self.server, self.port))
        if self.ssl:
            self.socket = wrap_socket(self.socket)
        if self.conf.get("password"):
            self.send("PASS {}".format(self.conf["password"]))
        self.send("USER {} 0 * :{}".format(self.user, self.gecos))
        if self.conf.get("sasl"):
            self.send("CAP REQ :multi-prefix sasl")
        self.send("NICK {}".format(self.nick))
        self.schedulePing()
        self.ibuffer = ""
        log.debug("(%s) Running main loop", self.netname)
        self.connected = True

    def disconnect(self, quit=None, terminate=True):
        self.send("QUIT :{}".format("Goodbye" if not quit else quit))
        self.connected = False
        self.socket.close()
        self.pingTimer.cancel()
        if terminate:
            sys.exit(0)

    def reconnect(self):
        self.socket.close()
        self.connected = False
        self.pingTimer.cancel()
        self.connect()

if __name__ == "__main__":

    try:
        config_file = sys.argv[1]
        global conf
        with open(config_file, 'r') as f:
            conf = json.load(f)

    except ValueError as e:
        log.critical("Error parsing config: {}".format(e))
        sys.exit(1)

    except FileNotFoundError as e:
        log.critical(e)
        sys.exit(1)

    except:
        log.critical("No config file supplied.")
        sys.exit(1)

    reload_handlers(init=True)

    for server in conf["servers"]:
        utils.connections[server["netname"]] = IRC(server)
    reload_plugins(init=True)
    connectall()
