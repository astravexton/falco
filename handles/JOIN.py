import fnmatch, time

def handle_JOIN(irc, args):
    chan = args.args[0]
    account = ""
    gecos = ""
    if len(args.args) > 1:
        account = args.args[1]
    if len(args.args) > 2:
        gecos = args.args[2]
    nick = args.sender.nick
    ident = args.sender.ident
    host = args.sender.mask

    chanObj = irc.get_channel(chan)
    if nick not in chanObj.members.keys():
        userObj = irc.get_user(nick)
        userObj.host = host
        userObj.user = ident
        userObj.gecos = gecos
        userObj.nickname = nick
        userObj.channels[chan] = chanObj
        chanObj.add_member(nick, userObj)
        irc.users[nick] = userObj
        if chan not in irc.conf.get("donotlog", []):
            userObj.lastaction = {"action": "JOIN", "args": None, "time": time.time(), "chan": chan}
