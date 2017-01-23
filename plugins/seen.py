from utils import add_cmd, timesince

@add_cmd
def seen(irc, source, msgtarget, args):
    nick = args.split()[0]
    try:
        for nicks in irc.nicks.keys():
            if nick.lower() == nicks.lower():
                n = irc.nicks[nicks]["lastaction"]
                break
        try:
            s = n
            n = irc.nicks[nick]
            if s["chan"] == nick: return
            if s["action"] == "PRIVMSG":
                irc.msg(msgtarget, "{} ({}@{}) was last seen saying \"{}\" about {} ago in {}".format(
                    nick, n["ident"], n["host"], s["args"].replace("", ""), timesince(s["time"]), s["chan"]))
            elif s["action"] == "JOIN":
                irc.msg(msgtarget, "{} ({}@{}) was seen joining {} about {} ago".format(
                    nick, n["ident"], n["host"], s["chan"], timesince(s["time"])))
            elif s["action"] == "PART":
                irc.msg(msgtarget, "{} ({}@{}) was seen parting {} about {} ago ({})".format(
                    nick, n["ident"], n["host"], s["chan"], timesince(s["time"]), s["args"] or ""))
            elif s["action"] == "QUIT":
                irc.msg(msgtarget, "{} ({}@{}) was seen quitting about {} ago ({})".format(
                    nick, n["ident"], n["host"], timesince(s["time"]), s["args"]))
            elif s["action"] == "KICK":
                irc.msg(msgtarget, "{} ({}@{}) was last seen kicked from {} about {} ago ({})".format(
                    nick, n["ident"], n["host"], s["chan"], timesince(s["time"]), s["args"]))
            elif s["action"] == "NICK":
                irc.msg(msgtarget, "{} ({}@{}) was last seen changing nick to {} about {} ago".format(
                    nick, n["ident"], n["host"], s["args"], timesince(s["time"])))

        except:
            if nick == irc.nick:
                irc.msg(msgtarget, "I'm right here!")
            else:
                irc.msg(msgtarget, "I don't know who that is")
    except KeyError:
        irc.msg(msgtarget, "I don't know who that is")
