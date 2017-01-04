import time

def handle_QUIT(irc, args):
    # args: ['Read error: Connection reset by peer']
    # source: InvGhost!~InvGhostt@hst-128-73.telelanas.lt

    nick = args.sender.nick
    ident = args.sender.ident
    host = args.sender.hostmask
    msg = args.args[0] or ""

    for chan in irc.nicks[nick]["channels"]:
        del irc.channels[chan]["nicks"][nick]

    irc.nicks[nick]["channels"] = []
    irc.nicks[nick]["lastaction"] = {"action": "QUIT", "args": msg, "time": time.time(), "chan": None}
