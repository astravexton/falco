import time

def handle_PART(irc, source, args):
    # args: ["#channel"]
    # source: |!Karkat@hide-A31D54D.zyr.io

    chan = args[0]
    nick = source.split("!")[0]
    ident = source.split("!")[1].split("@")[0]
    host = source.split("@")[1]

    if chan not in ["##chat-bridge"]:
        irc.nicks[nick]["lastaction"] = {"action": "PART", "args": args[1] if len(args) == 2 else "", "time": time.time(), "chan": chan}

    try:
        irc.nicks[nick]["channels"].remove(chan)
        del irc.channels[chan]["nicks"][nick]
    except KeyError:
        pass

