import re, time, threading, fnmatch
from utils import isAdmin, isOp, bot_regexes, bot_commands
from log import log

def handle_NOTICE(irc, args):
    chan, text = args.args
    nick = args.sender.nick
    ident = args.sender.ident
    address = args.sender.mask
    userObj = irc.get_user(nick)

    if userObj.ignored and not any([isOp(irc, args.sender), isAdmin(irc, args.sender)]):
        return

    if nick == irc.nick:
        log.info("Ignoring self")
        return # don't reply to self for PRIVMSG

    if chan == irc.nick:
        chan = nick

    chanObj = irc.get_channel(chan)

    if "\x01ACTION " in args.args[1]:
        _format = "* {nick} {message}".format(nick=nick, message=args.args[1].replace("\x01ACTION ","").replace("\x01", ""))
    else:
        _format = "<{nick}> {message}".format(nick=nick, message=args.args[1])

    if len(chanObj.buffer) > irc.buffermaxlen:
        chanObj.buffer.pop(0)
    chanObj.buffer.append((time.time(), _format))

    regex = u"(?:{})(.*?)(?:$|\s+)(.*)".format(irc.prefix)
    m = re.match(regex, text)
    if m:
        command, cmdargs = m.groups()
        if command in bot_commands.keys():
            # log.info("(%s) Calling command %r with args %r", irc.netname, command, cmdargs)
            irc.executor.submit(bot_commands[command], irc, chan, args, cmdargs)

    if chan not in irc.conf.get("donotlog", []):
        userObj = irc.get_user(nick)
        userObj.lastaction = {"action": "PRIVMSG", "args": args.args[1], "time": time.time(), "chan": chan}
