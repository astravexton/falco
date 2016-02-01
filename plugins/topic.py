from utils import *

@add_cmd
def topic(irc, source, msgtarget, args):
    if isAdmin(irc, source):
        topics = irc.channels[msgtarget]["topic"].split(" | ")
        while True:
            t = "{} | {}".format(args, irc.channels[msgtarget]["topic"])
            if len(t) > 307:
                t = t.split(" | ")[0:-1]
            else:
                break
        irc.chanmodes[msgtarget].append("TOPIC {} :{}".format(msgtarget, t))
        irc.send("PRIVMSG ChanServ :OP {}".format(msgtarget))
