def handle_NICK(irc, args):
    # source: nathan!nathan@392D2D96.A2275890.DCE72A8F.IP
    # args: ['nathanaan']

    oldnick = args.sender.nick
    newnick = args.args[0]

    if oldnick == irc.nick:
        irc.nick = newnick

    irc.nicks[oldnick]["lastaction"] = {"action": "NICK", "args": newnick, "time": time.time(), "chan": None}
    irc.nicks[newnick] = irc.nicks[oldnick]
    irc.nicks[newnick]["nick"] = newnick
    for chan in irc.nicks[newnick]["channels"]:
        if oldnick in irc.channels[chan]["nicks"].keys():
            irc.channels[chan]["nicks"][newnick] = irc.channels[chan]["nicks"][oldnick]
            del irc.channels[chan]["nicks"][oldnick]
        else:
            irc.send("WHO {}".format(newnick))
