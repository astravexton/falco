import json, random, subprocess, re, time, threading, fnmatch
from utils import connections, isAdmin, isOp, bot_regexes, timesince
from cgi import escape

def handle_NOTICE(irc, source, args):
    nick = source.split("!")[0]
    ident = source.split("!")[1].split("@")[0]
    address = source.split("@")[1]
    chan, message = args
    print(nick,message)

    #if nick == "NickServ" and "This nickname is registered." in message:
    #    if "nickserv_password" in irc.conf:
    #        irc.send("PRIVMSG NickServ :IDENTIFY {}".format(irc.conf["nickserv_password"]))
    #        time.sleep(3) # sleep to let it get a cloak
    #        # TODO: does this actually work?
    #        # TODO: SASL plugin..

def handle_PRIVMSG(irc, source, args):
    nick = source.split("!")[0]
    ident = source.split("!")[1].split("@")[0]
    address = source.split("@")[1]
    ignored = False
    try:
        chan, message = args
    except ValueError:
        return

    if chan == irc.nick:
        chan = nick

    for user in irc.ignored:
        if fnmatch.fnmatch(nick.lower(), user.lower()) == True:
            ignored = True
        elif fnmatch.fnmatch(address.lower(), user.lower()) == True:
            ignored = True
        elif chan.lower() == user.lower():
            ignored = True

    if isAdmin(irc, source) or isOp(irc, source):
        ignored = False

    if ignored == False:

        if "\x01ACTION " in message:
            _format = "* {nick} {message}".format(nick=nick, message=message.replace("\x01ACTION ","").replace("\x01", ""))
        else:
            _format = "<{nick}> {message}".format(nick=nick, message=message)

        try:
            if len(irc.channels[chan]["buffer"]) > irc.buffermaxlen:
                irc.channels[chan]["buffer"].pop(0)
            irc.channels[chan]["buffer"].append(_format)
        except:
            # buffer doesn't exist? usually a pm
            irc.channels[chan] = {"buffer": []}

        for cmd in bot_regexes.items():
            regex, func = cmd
            m = regex.search(message)
            if m:
                log.info("(%s) Calling regex for %s", irc.netname, func.__name__)
                c = threading.Thread(target=func, args=(irc, source, chan, m.groups()))
                c.daemon = True
                c.start()
                #return func(irc, source, chan, m.groups())


        # TODO: move relay to own plugin
        if irc.relay_enabled == True:
            if irc.relay_socket.connected == False:
                try:
                    irc.relay_socket.connect("ws://127.0.0.1:8888/ws/")
                    for chan in irc.relay_chans:
                        irc.relay_socket.send("TOPIC :{}".format(
                            irc.channels[chan]["topic"] if "topic" in irc.channels[chan] \
                                else "No topic has been set for {}".format(chan)))

                        nicks = " ".join(list(nick for nick in irc.channels[chan]["nicks"].keys()))
                        irc.relay_socket.send("NICKS {}".format(nicks))
                except ConnectionRefusedError:
                    irc.relay_enabled = False
            if chan != irc.nick and chan in irc.relay_chans:
                try:
                    irc.relay_socket.send(escape(_format))
                except BrokenPipeError as e:
                    for chan in irc.relay_chans:
                        #irc.msg(chan, "Relay disconnected: {}".format(e))
                        irc.relay_enabled == False
                        irc.relay_socket.close()
        elif irc.relay_enabled == False and irc.relay_socket.connected == True:
            irc.relay_socket.send("Relay disconnected")
            irc.srelay_socket.close()

        #text = re.sub(r"\$[a-z]+", subs, message, flags=re.IGNORECASE)
        #if text != message and message[0] not in ".!@:":
        #    irc.msg(chan, "│ "+text, reply="PRIVMSG")

        if args[0] == irc.nick:
            # in a pm, should reply to nick not self
            args[0] = source.split("!")[0]
            regex = u"(?:{}?)(.*?)(?:$|\s+)(.*)".format(irc.prefix)
        else:
            regex = u"(?:{})(.*?)(?:$|\s+)(.*)".format(irc.prefix)
        m = re.match(regex, message)
        if m:
            command, args = m.groups()

            try:
                func = utils.bot_commands[command]
            except KeyError:
                pass

            else:
                try:
                    log.info("(%s) Calling command %r", irc.netname, command)
                    threading.Thread(target=func, args=(irc, source, chan, args)).start()

                except Exception as e:
                    log.exception("(%s) Unhandled exception caught in command %r", irc.netname, command)
                    irc.msg(chan, "Uncaught exception: {}".format(str(e)))

        if chan not in ["##chat-bridge"]:
            try:
                irc.nicks[nick]["lastaction"] = {"action": "PRIVMSG", "args": message, "time": time.time(), "chan": chan}
                #irc.nicks[nick]["lastspoke"] = time.time()
                #irc.nicks[nick]["lastmsg"] = message
            except:
                pass

        # astra!nathan@meetmehereonirclo.lol ['#chat', 'test'] test #chat
        if source.startswith("MCRelay!"):
            msg = message.split("> ",1)
            if msg[1].startswith("`"):
                irc.send("PRIVMSG {} :{}".format(chan, msg[1]))
