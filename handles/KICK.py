def handle_KICK(irc, args):
    try:
        knick = args.sender.nick
    except AttributeError:
        knick = args.sender[1:]
    chan, nick, reason = args.args

    chanObj = irc.get_channel(chan)
    userObj = irc.get_user(nick)
    userObj.channels.remove(chan)
    del chanObj.members[nick]
    if chan not in irc.conf.get("donotlog", []):
        userObj.lastaction = {"action": "KICK", "args": "({}) {}".format(knick, reason), "time": time.time(), "chan": chan}
