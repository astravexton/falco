#!/usr/bin/python3
# -*- coding: utf-8 -*-
import glob, os, socket, time, re, sys, json
import threading
from ssl import wrap_socket
from log import log
import utils
import imp

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

def reload_config():
    for irc in utils.connections.values():
        if irc.conf_mtime != os.stat(config_file).st_mtime:
            with open(config_file, "r") as f:
                conf = json.load(f)
            irc.conf_mtime = os.stat(config_file).st_mtime
            irc.conf = conf[irc.netname]
            irc.reloadConfig()
            log.debug("(%s) Reloaded config", irc.netname)

def connectall():
    for server in utils.connections.values():
        server.start()

log.info("Starting falco")

mtimes = dict()

class IRC(threading.Thread):

    def __init__(self, conf, config_file):
        threading.Thread.__init__(self)
        #self.daemon         = True
        self.data_dir       = "data/"
        os.makedirs(self.data_dir, exist_ok=True)
        self.conf           = conf
        self.conf_mtime     = os.stat(config_file).st_mtime
        self.netname        = self.conf["netname"]
        self.rx             = 0
        self.tx             = 0
        self.txmsgs         = 0
        self.rxmsgs         = 0
        self.started        = 0
        self.server         = self.conf["server"]
        self.port           = self.conf["port"]
        self.ssl            = self.conf["ssl"]
        self.nick           = self.conf["nick"]
        self.pingfreq       = 30
        self.pingtimeout    = self.pingfreq*2
        self.pingwarn       = 5
        self.password       = "6675636b796f75"
        self.prefixmodes    = {'q': '~', 'a': '&', 'v': '+', 'o': '@', 'h': '%'}
        self.connected      = False
        self.chanmodes      = {}
        self.modes          = []
        self.hasink         = True
        self.color          = 14
        self.buffermaxlen   = 16003
        self.identified     = False
        self.cap            = []
        self.capdone        = False
        try:
            self.nicks      = json.load(open("data/{}-nicks.json".format(self.netname)))
            self.channels   = json.load(open("data/{}-channels.json".format(self.netname)))
        except FileNotFoundError: 
            self.channels       = {}
            self.nicks          = {}
        except json.decoder.JSONDecodeError as e:
            sys.exit("{} - {}".format(e, self.netname))
        self.title_snarfer_allowed      = []
        self.title_snarfer_ignored_urls = []

        self.pingTimer = None
        self.pingtime = time.time()
        self.lastping = self.pingtime

        self.reloadConfig()

    def reloadConfig(self):

        self.reply          = self.conf["reply"]
        self.user           = self.conf["ident"]
        self.gecos          = self.conf["gecos"]
        self.setmodes       = self.conf["modes"]
        self.prefix         = self.conf["prefix"]
        self.admins         = self.conf["admins"]
        self.autojoin       = self.conf["autojoin"]
        self.ignored        = self.conf["ignored"]
        self.autokick       = self.conf["autokick"]
        self.ops            = self.conf.get("ops", [])

    def run(self):
 
        self.connect()

        self.connected = True
        while self.connected:
            try:
                data = utils.decode(self.socket.recv(2048))
                self.ibuffer += data
                while "\r\n" in self.ibuffer:
                    reload_handlers()
                    reload_plugins()
                    reload_config()

                    line, self.ibuffer = self.ibuffer.split("\r\n", 1)
                    line = line.strip()
                    
                    
                    try:
                        func = globals()["handle_"+utils.parseArgs(line).type]
                    except KeyError:
                        log.warn("No handler for %s found", utils.parseArgs(line).type)
                    else:
                        func(self, utils.parseArgs(line))

                    log.debug("(%s) -> %s", self.netname, line)

                    self.rx += len(line)
                    self.rxmsgs += 1

                    args = line.split(" ")

                    if not args:
                        return

                    if args[1] == "PONG":
                        self.pingtime = int(time.time() - self.lastping)
                        self.lastping = time.time()

                        if self.pingtime - self.pingfreq > self.pingwarn:
                            log.warn("(%s) Lag: %s seconds", self.netname,
                                        round(self.pingtime - self.pingfreq, 3))

            except KeyboardInterrupt:
                self.pingTimer.stop()
                self.schedulePing() # writes nicks and channels to files,
                                    # will be moved to own function eventually
                self.disconnect("CTRL-C at console.")

    def msg(self, target, message, reply=None):
        reply = self.reply if not reply else reply
        if self.hasink:
            self.send("{} {} :\x03{}│\x0f {}".format(reply, target, self.color, message))
        else:
            self.send("{} {} :{}".format(reply, target, message))
        time.sleep(0.3)

    def kick(self, chan, target, message="Goodbye"):
        self.send("KICK {} {} :{}".format(chan, target, message))

    def send(self, data):
        data = data.replace('\n', ' ').replace("\a", "")
        data = data.encode("utf-8") + b"\r\n"
        stripped_data = data.decode("utf-8").strip("\n")
        log.debug("(%s) <- %s", self.netname, stripped_data)
        self.tx += len(data)
        self.txmsgs += 1
        try:
            self.socket.send(data)
        except AttributeError:
            log.debug("(%s) Dropping message %r; network isn't connected!", self.netname, stripped_data)

    def schedulePing(self):
        with open(self.data_dir+self.netname+"-nicks.json", "w") as f:
            json.dump(self.nicks, f, indent=4)
        with open(self.data_dir+self.netname+"-channels.json", "w") as f:
            json.dump(self.channels, f, indent=4)
        #if time.time() - self.lastping > self.pingtimeout:
        #    self.disconnect("Ping timeout: {} seconds".format(round(self.pingtime - self.pingfreq)))
        #    self.run()
        #self.send("PING {}".format(time.time()))
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
        self.send("CAP LS")
        if self.conf.get("password"):
            self.send("PASS {}".format(self.conf["password"]))
        self.send("USER {} 0 * :{}".format(self.user, self.gecos))
        self.send("NICK {}".format(self.nick))
        self.ibuffer = ""
        log.debug("(%s) Running main loop", self.netname)
        self.schedulePing() # this seems to not work as expected, will fix at some point

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
        self.run()

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

    try:
        for server in conf.values():
            utils.connections[server["netname"]] = IRC(server, config_file)
        reload_plugins(init=True)
        connectall()
    except KeyboardInterrupt:
        print(" - exiting")
