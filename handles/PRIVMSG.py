import json, random, subprocess, re, time, threading, fnmatch
from utils import connections, isAdmin, isOp, bot_regexes, timesince
from cgi import escape

def handle_NOTICE(irc, args):
    pass

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

    if isAdmin(irc, args.sender) or isOp(irc, args.sender):
        ignored = False

    if ignored == False:
        chanObj = irc.get_channel(chan)

        if "\x01ACTION " in message:
            _format = "* {nick} {message}".format(nick=nick, message=message.replace("\x01ACTION ","").replace("\x01", ""))
        else:
            _format = "<{nick}> {message}".format(nick=nick, message=message)

        try:
            if len(chanObj.buffer) > irc.buffermaxlen:
                chanObj.buffer.pop(0)
            chanObj.buffer.append((time.time(), _format))
        except:
            # buffer doesn't exist? usually a pm
            pass
            #irc.channels[chan] = {"buffer": []}

        for cmd in bot_regexes.items():
            regex, func = cmd
            m = regex.search(message)
            if m:
                log.debug("(%s) Calling regex for %s", irc.netname, func.__name__)
                c = threading.Thread(target=func, args=(irc, args.sender, chan, m.groups()))
                c.daemon = True
                c.start()

        if args.args[0] == irc.nick:
            # in a pm, should reply to nick not self
            args.args[0] = nick
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
                    log.debug("(%s) Calling command %r", irc.netname, command)
                    threading.Thread(target=func, args=(irc, args.sender, chan, cmdargs)).start()

                except Exception as e:
                    log.exception("(%s) Unhandled exception caught in command %r", irc.netname, command)
                    irc.msg(chan, "Uncaught exception: {}".format(str(e)))

        if chan not in irc.conf.get("donotlog", []):
            if chan != irc.nick: # dont log self
                userObj = irc.get_user(nick)
                userObj.lastaction = {"action": "PRIVMSG", "args": message, "time": time.time(), "chan": chan}