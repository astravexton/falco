#!/usr/bin/python3
import conf, glob, os, socket, time, re, string, sys, json
import threading
import queue as Queue
from conf import conf
from ssl import wrap_socket
from log import log
import utils
import imp
from multiprocessing import Process
import hashlib, binascii

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
    for plugin in conf.get("plugins"):
        _plugin = os.path.join(os.getcwd(), "plugins/{}.py".format(plugin))
        mtime = os.stat(_plugin).st_mtime
        if mtime != mtimes.get(_plugin):
            mtimes[_plugin] = mtime
            try:
                moduleinfo = imp.find_module(plugin, plugins_folder)
                pl = imp.load_source(plugin, moduleinfo[1])
            except ImportError as e:
                if str(e).startswith('No module named'):
                    log.error('Failed to load plugin %r: the plugin could not be found.', plugin)
                else:
                    log.error('Failed to load plugin %r: import error %s', plugin, str(e))
                    if init:
                        sys.exit(1)
            else:
                if hasattr(pl, 'main'):
                    log.debug('Calling main() function of plugin %r', pl)
                    pl.main()
            log.info("(Re)Loaded %s", _plugin)

def reload_config(irc):
    if irc.conf_mtime != os.stat("config.json").st_mtime:
        with open("config.json", "r") as f:
            conf = json.load(f)
        irc.conf_mtime = os.stat("config.json").st_mtime
        irc.conf = conf["servers"][irc.netname]
        irc.bot["prefix"] = irc.conf["prefix"]
        irc.bot["admins"] = irc.conf["admins"]
        log.debug("(%s) Reloaded config", irc.netname)

log.info("Starting falco")

mtimes = dict()

class IRC():

    def __init__(self, netname, conf):
        self.conf                  = conf
        self.bot                   = dict()
        self.server                = dict()
        self.stats                 = dict()
        self.conf_mtime            = os.stat("config.json").st_mtime
        self.netname               = netname

        self.server["host"]        = self.conf["server"]
        self.server["port"]        = self.conf["port"]
        self.server["ssl"]         = self.conf["ssl"]
        self.server["pingfreq"]    = 30
        self.server["pingtimeout"] = 60
        self.server["pingwarn"]    = 5
        self.server["password"]    = "6675636b796f75"
        self.server["prefixmodes"] = {"o":"@", "v":"+"}
        self.server["connected"]   = False
        self.server["process"]     = None

        self.stats["rx"]           = 0
        self.stats["tx"]           = 0
        self.stats["txmsgs"]       = 0
        self.stats["rxmsgs"]       = 0
        self.stats["started"]      = time.time()

        self.bot["nick"]           = self.conf["nick"]
        self.bot["user"]           = self.conf["ident"]
        self.bot["gecos"]          = self.conf["gecos"]
        self.bot["modes"]          = self.conf["modes"]
        self.bot["prefix"]         = self.conf["prefix"]
        self.bot["admins"]         = self.conf["admins"]
        self.bot["autojoin"]       = self.conf["autojoin"]
        self.bot["channels"]       = dict()
        self.bot["nicks"]          = dict()
        self.bot["hasink"]         = True
        self.bot["color"]          = 14
        self.bot["buffermaxlen"]   = 16000
        self.bot["autokick"]       = dict()

        self.auth                  = dict()
        self.auth["nathan"]        = {"password": "", "salt": ""}

        self.pingTimer             = None
        self.pingtime              = time.time()
        self.lastping              = self.pingtime

        if self.conf["active"]:
            self.run()

    def run(self):
        #threading.Thread(target=self.connect).start()
        self.server["process"] = Process(target=self.connect, name="Bot-Thread")
        self.server["process"].start()
        self.server["process"].join()

    def msg(self, target, message, reply="NOTICE"):
        if self.bot["hasink"]:
            self.send("{} {} :\x03{}{}".format(reply, target, self.bot["color"], message))
        else:
            self.send("{} {} :{}".format(reply, target, message))

    def kick(self, chan, target, message="Goodbye"):
        self.send("KICK {} {} :{}".format(chan, target, message))

    def join(self, chan):
        self.send("JOIN {}".format(chan))

    def send(self, data, *kw):
        print(data, kw)
        data = data.replace('\n', ' ') % kw
        data = data.encode("utf-8") + b"\n"
        stripped_data = data.decode("utf-8").strip("\n")
        if "PASS " not in stripped_data: # don't print PASS output
            log.debug("(%s) <- %s", self.netname, stripped_data)
        self.stats["tx"] += len(data)
        self.stats["txmsgs"] += 1
        try:
            self.socket.send(data)
        except AttributeError:
            log.debug("(%s) Dropping message %r; network isn't connected!", self.netname, stripped_data)

    def schedulePing(self):
        self.send("PING {}".format(time.time()))
        self.pingTimer = threading.Timer(self.pingfreq, self.schedulePing)
        self.pingTimer.daemon = True
        self.pingTimer.start()

    def connect(self):
        if self.server["connected"]:
            self.msg("#programming", "I am already connected, dumbass")
            return
        log.debug("(%s) Attempting to connect to %s/%s as %s",
                  self.netname, self.server["host"], self.server["port"], self.bot["nick"])
        self.socket = socket.create_connection((self.server["host"], self.server["port"]))
        if self.server["ssl"]:
            self.socket = wrap_socket(self.socket)
        if self.conf.get("password"):
            self.send("PASS {}".format(self.conf["password"]))
        self.send("USER {} 0 * :{}".format(self.bot["user"], self.bot["gecos"]))
        self.send("NICK {}".format(self.bot["nick"]))
        #self.schedulePing()
        ibuffer = ""
        log.debug("(%s) Running main loop", self.netname)
        self.server["connected"] = True
        while True:
            if self.server["connected"]:
                try:
                    data = utils.decode(self.socket.recv(2048))
                    ibuffer += data
                    while "\r\n" in ibuffer:
                        reload_handlers()
                        reload_plugins()
                        reload_config(self)

                        line, ibuffer = ibuffer.split("\r\n", 1)
                        line = line.strip()
                        log.debug("(%s) -> %s", self.netname, line)
                        self.stats["rx"] += len(line)
                        self.stats["rxmsgs"] += 1

                        args = line.split(" ")

                        if not args:
                            return

                        elif args[0] == "PING":
                            #self.send("LUSERS")
                            self.send("PONG {}".format(args[1]))

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

                            if command == "PRIVMSG":
                                msgtarget = args[0] if args[0] != self.bot["nick"] else user.split("!")[0]
                                command = ""
                                regex = u"(?:{})(.*?)(?:$|\s+)(.*)".format(self.bot["prefix"])
                                m = re.match(regex, " ".join(args[1:]))
                                if m:
                                    command, args = m.groups()

                                    try:
                                        func = utils.bot_commands[command]
                                    except KeyError:
                                        pass

                                    else:
                                        try:
                                            log.info("(%s) Calling command %r", self.netname, command)
                                            threading.Thread(target=func, args=(self, user, msgtarget, args)).start()

                                        except Exception as e:
                                            log.exception("(%s) Unhandled exception caught in command %r", self.netname, command)
                                            self.msg(msgtarget, "Uncaught exception: {}".format(str(e)))

                        except IndexError:
                            continue

                except KeyboardInterrupt:
                    self.disconnect("CTRL-C at console.")

                except socket.error as e:
                    log.critical("(%s) Received socket error: '%s', aborting!", self.netname, e)
                    sys.exit(1)

            else:
                self.socket.shutdown(2)
                self.socket.close()
                sys.exit(1)

    def disconnect(self, quit=None, terminate=True):
        self.send("QUIT :{}".format("Goodbye" if not quit else quit))
        self.connected = False
        self.socket.shutdown(2)
        self.socket.close()
        if terminate:
            sys.exit(0)

    def reconnect(self):
        self.disconnect(terminate=False)
        self.server["connected"] = False
        #self.pingTimer.cancel()
        self.connect()

if __name__ == "__main__":
    reload_handlers(True)
    reload_plugins(True)
    for network in conf.get("servers"):
        utils.connections[network] = IRC(network, conf["servers"][network])
        #utils.connections[network] = threading.Thread(target=IRC, args=(network, conf.get("servers").get(network)))
        #utils.connections[network].start()
