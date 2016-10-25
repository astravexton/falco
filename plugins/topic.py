from utils import *

@add_cmd
def topic(irc, source, msgtarget, args):
    "topic <topic> -- appends <topic> to the current channel topic"
    if isAdmin(irc, source):
        if args:
            topic = irc.channels[msgtarget]["topic"]
            t = "{} | {}".format(args, topic)
            while True:
                if len(t) > irc.topiclen:
                    t = " | ".join(t.split(" | ")[0:-1])
                else:
                    break
            irc.chanmodes[msgtarget].append("TOPIC {} :{}".format(msgtarget, t))
            irc.send("PRIVMSG ChanServ :OP {}".format(msgtarget))
        else:
            irc.msg(msgtarget, "topic <topic> -- appends <topic> to the current channel topic")
