import time

def handle_QUIT(irc, args):
    # args: ['Read error: Connection reset by peer']

    nick = args.sender.nick
    ident = args.sender.ident
    host = args.sender.hostmask
    msg = args.args[0] or ""

    userObj = irc.get_user(nick)
    for channel in userObj.channels:
        del irc.get_channel(channel).members[nick]

    userObj.channels = []
    userObj.lastaction = {"action": "QUIT", "args": msg, "time": time.time(), "chan": None}
