from utils import *

@add_cmd
def topic(irc, source, msgtarget, args):
    topics = irc.channels[msgtarget]["topic"].split(" | ")
    while topics:
        t = "{} | {}".format(args, topics.pop(0))
        print(t)
        if len(t) < 307:
            topic = t
        else:
            break
    irc.send("TOPIC {} :{}".format(msgtarget, topic))
