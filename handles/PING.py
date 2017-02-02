def handle_PING(irc, args):
    irc.send("PONG :{}".format(args.args))