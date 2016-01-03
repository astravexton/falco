from utils import add_cmd, timesince

#@add_cmd
#def seen(irc, source, msgtarget, args):
#    nick = args.split()[0]
#    try:
#        irc.msg(msgtarget, "{} was last seen saying \"{}\" about {} ago".format(
#                args, irc.nicks[nick]["lastmsg"].replace("\x01", ""), timesince(irc.nicks[nick]["lastspoke"])))
#    except KeyError as e:
#        irc.msg(msgtarget, "I haven't seen {} around.".format(nick))

@add_cmd
def seen(irc, source, msgtarget, args):
    nick = args.split()[0]
    for nicks in irc.nicks.keys():
        if nick.lower() == nicks.lower():
            n = irc.nicks[nicks]["lastaction"]
    try:
        #s = irc.nicks[nick]["lastaction"]
        s = n
        n = irc.nicks[nick]
        if s["chan"] == nick: return
        if s["action"] == "PRIVMSG":
            irc.msg(msgtarget, "{} ({}@{}) was last seen saying \"{}\" about {} ago in {}".format(
                nick, n["ident"], n["host"], s["args"].replace("\x01", ""), timesince(s["time"]), s["chan"]))
        elif s["action"] == "JOIN":
            irc.msg(msgtarget, "{} ({}@{}) was seen joining {} about {} ago".format(
                nick, n["ident"], n["host"], s["chan"], timesince(s["time"])))
        elif s["action"] == "PART":
            irc.msg(msgtarget, "{} ({}@{}) was seen parting {} about {} ago ({})".format(
                nick, n["ident"], n["host"], s["chan"], timesince(s["time"]), s["args"] or ""))
        elif s["action"] == "QUIT":
            irc.msg(msgtarget, "{} ({}@{}) was seen quitting about {} ago ({})".format(
                nick, n["ident"], n["host"], timesince(s["time"]), s["args"]))

    except:
        if nick == irc.nick:
            irc.msg(msgtarget, "I'm right here!")
        else:
            irc.msg(msgtarget, "I don't know who that is")
