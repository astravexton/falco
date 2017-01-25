
def handle_TOPIC(irc, args):
    chan, topic = args.args
    chanObj = irc.get_channel(chan)
    chanObj.append_old_topic(chanObj.topic)
    chanObj.topic = topic
    # irc.channels[chan]["topic"] = topic
