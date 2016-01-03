import time

def handle_QUIT(irc, source, args):
    # args: ['Read error: Connection reset by peer']
    # source: InvGhost!~InvGhostt@hst-128-73.telelanas.lt

    nick = source.split("!")[0]
    ident = source.split("!")[1].split("@")[0]
    host = source.split("@")[1]
    msg = args[0] or ""

    irc.nicks[nick]["lastaction"] = {"action": "QUIT", "args": msg, "time": time.time(), "chan": None}

