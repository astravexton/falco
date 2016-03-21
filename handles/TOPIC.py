
def handle_TOPIC(irc, args):
    chan, topic = args.args
    irc.channels[chan]["topic"] = topic
