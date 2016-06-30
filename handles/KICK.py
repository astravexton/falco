def handle_KICK(irc, args):
    try:
        knick = args.sender.nick
    except AttributeError:
        knick = args.sender[1:]
    chan, nick, reason = args.args
    if chan in irc.nicks[nick]["channels"]:
        irc.nicks[nick]["channels"].remove(chan)
    if chan not in irc.conf.get("donotlog", []):
        irc.nicks[nick]["lastaction"] = {
            "action": "KICK",
            "args": "({}) {}".format(knick, reason),
            "time": time.time(),
            "chan": chan
        }
