
def handle_TOPIC(irc, source, args):
    chan, topic = args
    set_by = source
    irc.channels[chan]["topic"] = topic
