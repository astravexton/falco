import time

def handle_PART(irc, args):
    # args: ["#channel"]
    # source: |!Karkat@hide-A31D54D.zyr.io

    chan = args.args[0]
    nick = args.sender.nick
    ident = args.sender.ident
    host = args.sender.hostmask

    if chan not in irc.conf.get("donotlog", []):
        irc.nicks[nick]["lastaction"] = {"action": "PART", "args": args[1] if len(args) == 2 else "", "time": time.time(), "chan": chan}

    try:
        irc.nicks[nick]["channels"].remove(chan)
        del irc.channels[chan]["nicks"][nick]
    except KeyError:
        pass

