from utils import *

@add_cmd
def topic(irc, source, msgtarget, args):
    topics = irc.channels[msgtarget]["topic"].split(" | ")
    while True:
        t = "new topic | {}".format(topic)
        if len(t) > 307:
            t = t.split(" | ")[0:-1]
        else:
            break
    irc.send("TOPIC {} :{}".format(msgtarget, t))
