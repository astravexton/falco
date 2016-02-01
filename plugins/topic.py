from utils import *

@add_cmd
def topic(irc, source, msgtarget, args):
    if isAdmin(irc, source):
        topic = irc.channels[msgtarget]["topic"]
        t = "{} | {}".format(args, topic)
        while True:
            if len(t) > 307:
                t = " | ".join(t.split(" | ")[0:-1])
            else:
                break
        irc.chanmodes[msgtarget].append("TOPIC {} :{}".format(msgtarget, t))
        irc.send("PRIVMSG ChanServ :OP {}".format(msgtarget))
