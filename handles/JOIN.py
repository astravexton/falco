import fnmatch, time

def handle_JOIN(irc, args):

    chan = args.args[0]
    nick = args.sender.nick
    ident = args.sender.ident
    host = args.sender.mask

    irc.chanmodes[chan] = list()

    if chan not in irc.channels:
        irc.channels[chan] = {
            "modes": (),
            "nicks": dict(),
            "buffer": [],
            "autojoin": False
        }

    if nick not in irc.nicks:
        irc.nicks[nick] = {
            "nick": nick,
            "ident": ident,
            "host": host,
            "gecos": None,
            "channels": list(),
            "server": None
        }
    elif nick in irc.nicks:
        irc.nicks[nick]["ident"] = ident
        irc.nicks[nick]["host"] = host
    try:
        irc.nicks[nick]["channels"].append(chan)
    except:
        print("{} not in irc.nicks".format(nick))

    if chan not in irc.autokick:
        irc.autokick[chan] = list()

    irc.channels[chan]["nicks"][nick] = ""

    if chan not in irc.conf.get("donotlog", []):
        irc.nicks[nick]["lastaction"] = {"action": "JOIN", "args": None, "time": time.time(), "chan": chan}

    if chan in irc.autokick:
        for user in irc.autokick[chan]:
            if fnmatch.fnmatch(source, user) or fnmatch.fnmatch(source.split("!")[0], user):
                irc.chanmodes[chan].append("KICK {} {} :Goodbye (autokick)".format(chan, source.split("!")[0]))
                irc.send("PRIVMSG ChanServ :OP {}".format(chan))
