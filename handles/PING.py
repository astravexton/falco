def handle_PING(irc, args):
    irc.send("PONG :{}".format(args.args[0] if args.args else ""))