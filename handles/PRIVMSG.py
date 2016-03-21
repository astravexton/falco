import json, random, subprocess, re, time, threading, fnmatch
from utils import connections, isAdmin, isOp, bot_regexes, timesince
from cgi import escape

def handle_NOTICE(irc, args):
    # args: .sender, .type, .args
    #print(args.sender)
    
    """
    # falco falco xe421.at.zyr.io astra test
    nick = source.split("!")[0]
    ident = source.split("!")[1].split("@")[0]
    address = source.split("@")[1]
    chan, message = args

    if nick == "NickServ" and irc.identified == False:
        if "This nickname is registered." in message:
            irc.send("PRIVMSG NickServ :identify {}".format(irc.conf["nickserv_password"]))
        elif "You are now identified" in message:
            irc.identified = True
            for chan in irc.channels:
                if irc.channels[chan]["autojoin"]:
                    irc.send("JOIN {}".format(chan))
    """

def handle_PRIVMSG(irc, args):
    nick = args.sender.nick
    ident = args.sender.ident
    address = args.sender.mask
    ignored = False
    try:
        chan, message = args.args
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

    if isAdmin(irc, args.sender.hostmask) or isOp(irc, args.sender.hostmask):
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
            pass
            #irc.channels[chan] = {"buffer": []}

        for cmd in bot_regexes.items():
            regex, func = cmd
            m = regex.search(message)
            if m:
                #log.info("(%s) Calling regex for %s", irc.netname, func.__name__)
                c = threading.Thread(target=func, args=(irc, args.sender.hostmask, chan, m.groups()))
                c.daemon = True
                c.start()

        if args.args[0] == irc.nick:
            # in a pm, should reply to nick not self
            args.args[0] = nick
            regex = u"(?:{}?)(.*?)(?:$|\s+)(.*)".format(irc.prefix)
        else:
            regex = u"(?:{})(.*?)(?:$|\s+)(.*)".format(irc.prefix)
        m = re.match(regex, message)
        if m:
            command, cmdargs = m.groups()

            if chan in irc.conf["blacklisted_commands"]:
                if command in irc.conf["blacklisted_commands"][chan]:
                    return

            try:
                func = utils.bot_commands[command]
            except KeyError:
                pass

            else:
                try:
                    #log.info("(%s) Calling command %r", irc.netname, command)
                    threading.Thread(target=func, args=(irc, args.sender.hostmask, chan, cmdargs)).start()

                except Exception as e:
                    log.exception("(%s) Unhandled exception caught in command %r", irc.netname, command)
                    irc.msg(chan, "Uncaught exception: {}".format(str(e)))

        if chan not in irc.conf.get("donotlog", []):
            try:
                irc.nicks[nick]["lastaction"] = {"action": "PRIVMSG", "args": message, "time": time.time(), "chan": chan}
            except:
                pass
