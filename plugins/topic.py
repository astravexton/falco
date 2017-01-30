from utils import *

@add_cmd
def topic(irc, target, args, cmdargs):
    "topic <topic>"
    if not isAdmin(irc, args.sender):
        return

    if not cmdargs:
        irc.msg(target, "topic <topic>")
        return

    topic = irc.get_channel(target).topic
    t = "{} | {}".format(cmdargs, topic) if topic else cmdargs
    while True:
        if not len(t) > irc.topiclen:
            break
        t = " | ".join(t.split(" | ")[0:-1])

    if irc.channels[target]["nicks"][irc.nick] == "o":
        irc.send("TOPIC {} :{}".format(target, t))
    else:
        irc.chanmodes[target].append("TOPIC {} :{}".format(target, t))
        irc.send("PRIVMSG ChanServ :OP {}".format(target))
