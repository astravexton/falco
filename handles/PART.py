import time

def handle_PART(irc, args):
    # args: ["#channel"]
    chan = args.args[0]
    nick = args.sender.nick
    ident = args.sender.ident
    host = args.sender.hostmask
    chanObj = irc.get_channel(chan)
    userObj = irc.get_user(nick)
    chanObj.remove_member(userObj)
    userObj.remove_channel(chan)
    if chan not in irc.conf.get("donotlog", []):
        reason = args.args[1] if len(args.args) > 1 else ""
        userObj.lastaction = {"action": "PART", "args": reason, "time": time.time(), "chan": chan}
