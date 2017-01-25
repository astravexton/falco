import time

def handle_QUIT(irc, args):
    # args: ['Read error: Connection reset by peer']
    nick = args.sender.nick
    ident = args.sender.ident
    host = args.sender.hostmask
    msg = args.args[0] or ""

    userObj = irc.get_user(nick)
    channels = userObj.channels.values()
    for channel in channels:
        channel.remove_member(userObj)
    
    userObj.channels = {}
    userObj.lastaction = {"action": "QUIT", "args": msg, "time": time.time(), "chan": None}
