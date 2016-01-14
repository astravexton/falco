import json, random, subprocess, re, time, threading, fnmatch
from utils import connections, isAdmin, isOp, bot_regexes, timesince
from cgi import escape

def handle_NOTICE(irc, source, args):
    nick = source.split("!")[0]
    ident = source.split("!")[1].split("@")[0]
    address = source.split("@")[1]
    chan, message = args

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

            if chan in irc.conf["blacklisted_commands"]:
                if command in irc.conf["blacklisted_commands"][chan]:
                    return

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
