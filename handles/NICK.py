def handle_NICK(irc, source, args):
    # source: nathan!nathan@392D2D96.A2275890.DCE72A8F.IP
    # args: ['nathanaan']
    oldnick, host = source.split("!"), source.split("@")[1]
    oldnick, ident = oldnick[0], oldnick[1].split("@")[0]
    newnick = args[0]

    if oldnick == irc.nick:
        irc.nick = newnick

    irc.nicks[newnick] = irc.nicks[oldnick]
    irc.nicks[newnick]["nick"] = newnick
    for chan in irc.nicks[newnick]["channels"]:
        try:
            irc.channels[chan]["nicks"][newnick] = irc.channels[chan]["nicks"][oldnick]
        except KeyError:
            irc.send("WHO {}".format(newnick))
