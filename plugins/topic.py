from utils import *

@add_cmd
def topic(irc, source, msgtarget, args):
    "topic <topic> -- appends <topic> to the current channel topic"
    if isAdmin(irc, source):
        if args:
            topic = irc.channels[msgtarget]["topic"] if "topic" in irc.channels[msgtarget].keys() else ""
            t = "{} | {}".format(args, topic) if topic else args
            while True:
                if len(t) > irc.topiclen:
                    t = " | ".join(t.split(" | ")[0:-1])
                else:
                    break
            if irc.channels[msgtarget]["nicks"][irc.nick] == "o":
                irc.send("TOPIC {} :{}".format(msgtarget, t))
            else:
                irc.chanmodes[msgtarget].append("TOPIC {} :{}".format(msgtarget, t))
                irc.send("PRIVMSG ChanServ :OP {}".format(msgtarget))
        else:
            irc.msg(msgtarget, "topic <topic> -- appends <topic> to the current channel topic")
