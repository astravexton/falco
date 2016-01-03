import fnmatch, time

def handle_JOIN(irc, source, args):
    # args: ["#channel"]
    # source: |!Karkat@hide-A31D54D.zyr.io
    #if source.split("!")[0] != irc.bot["nick"]:
    #    irc.send("WHOWAS {}".format(source.split("!")[0]))

    chan = args[0]
    nick = source.split("!")[0]
    ident = source.split("!")[1].split("@")[0]
    host = source.split("@")[1]

    irc.chanmodes[chan] = list()

    if chan not in irc.channels:
        irc.channels[chan] = {
            "modes": (),
            "nicks": dict(),
            "buffer": []}

    if nick not in irc.nicks:
        irc.nicks[nick] = {
            "nick": nick,
            "ident": ident,
            "host": host,
            "gecos": None,
            "channels": set(),
            "server": None
        }
    elif nick in irc.nicks:
        irc.nicks[nick]["ident"] = ident
        irc.nicks[nick]["host"] = host
    try:
        irc.nicks[nick]["channels"].add(chan)
    except:
        print(irc.nicks[nick])

    if chan not in irc.autokick:
        irc.autokick[chan] = list()

    irc.channels[chan]["nicks"][nick] = ""

    if chan not in ["##chat-bridge"]:
        irc.nicks[nick]["lastaction"] = {"action": "JOIN", "args": None, "time": time.time(), "chan": chan}

    if chan in irc.autokick:
        for user in irc.autokick[chan]:
            if fnmatch.fnmatch(source, user) or fnmatch.fnmatch(source.split("!")[0], user):
                irc.chanmodes[chan].append("KICK {} {} :Goodbye (autokick)".format(chan, source.split("!")[0]))
                irc.send("PRIVMSG ChanServ :OP {}".format(chan))
