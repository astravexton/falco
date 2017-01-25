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
    if chan not in irc.conf.get("donotlog", []):
        userObj.lastaction = {"action": "PART", "args": args.args[1], "time": time.time(), "chan": chan}
