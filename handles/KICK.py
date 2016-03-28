def handle_KICK(irc, args):
    chan, nick, reason = args.args
    if chan in irc.nicks[nick]["channels"]:
        irc.nicks[nick]["channels"].remove(chan)
    if chan not in irc.conf.get("donotlog", []):
        irc.nicks[nick]["lastaction"] = {
            "action": "KICK",
            "args": "({}) {}".format(args.sender.nick, reason),
            "time": time.time(),
            "chan": chan
        }
