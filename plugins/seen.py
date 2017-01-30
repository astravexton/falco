from utils import add_cmd, timesince

@add_cmd
def seen(irc, target, args, cmdargs):
    if not cmdargs:
        irc.msg(target, "seen <nick>")
        return

    nickObj = irc.get_user(cmdargs)
    lastaction = nickObj.lastaction
    if lastaction["time"] == 0:
        if nickObj.nickname != irc.nick:
            irc.msg(target, "I haven't seen that user before")
        else:
            irc.msg(target, "I'm right here!")
        return

    if nickObj.nickname == target:
        irc.msg(target, "{} ({}) was last seen sending me a pm about {} ago".format(
            nickObj.nickname, nickObj.prefix, timesince(lastaction["time"])))
        return

    if lastaction["action"] == "PRIVMSG":
        irc.msg(target, "{} ({}) was last seen saying \"{}\" about {} ago in {}".format(
            nickObj.nickname, nickObj.prefix, lastaction["args"], timesince(lastaction["time"]), lastaction["chan"]))

    elif lastaction["action"] == "JOIN":
        irc.msg(target, "{} ({}) was seen joining {} about {} ago".format(
            nickObj.nickname, nickObj.prefix, lastaction["chan"], timesince(lastaction["time"])))

    elif lastaction["action"] == "PART":
        irc.msg(target, "{} ({}) was seen parting {} about {} ago ({})".format(
            nickObj.nickname, nickObj.prefix, lastaction["chan"], timesince(lastaction["time"]), lastaction["args"] or ""))

    elif lastaction["action"] == "QUIT":
        irc.msg(target, "{} ({}) was seen quitting about {} ago ({})".format(
            nickObj.nickname, nickObj.prefix, timesince(lastaction["time"]), lastaction["args"]))

    elif lastaction["action"] == "KICK":
        irc.msg(target, "{} ({}) was last seen kicked from {} about {} ago ({})".format(
            nickObj.nickname, nickObj.prefix, lastaction["chan"], timesince(lastaction["time"]), lastaction["args"]))

    elif lastaction["action"] == "NICK":
        irc.msg(target, "{} ({}) was last seen changing nick to {} about {} ago".format(
            nickObj.nickname, nickObj.prefix, lastaction["args"], timesince(lastaction["time"])))
