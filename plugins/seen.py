from utils import add_cmd, pretty_date

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
        irc.msg(target, "{} ({}) was last seen sending me a pm {}".format(
            nickObj.nickname, nickObj.prefix, pretty_date(lastaction["time"])))
        return

    if lastaction["action"] == "PRIVMSG":
        irc.msg(target, "{} ({}) was last seen saying \"{}\" {} in {}".format(
            nickObj.nickname, nickObj.prefix, lastaction["args"], pretty_date(lastaction["time"]), lastaction["chan"]))

    elif lastaction["action"] == "JOIN":
        irc.msg(target, "{} ({}) was seen joining {} {}".format(
            nickObj.nickname, nickObj.prefix, lastaction["chan"], timesince(lastaction["time"])))

    elif lastaction["action"] == "PART":
        irc.msg(target, "{} ({}) was seen parting {} {} ({})".format(
            nickObj.nickname, nickObj.prefix, lastaction["chan"], pretty_date(lastaction["time"]), lastaction["args"] or ""))

    elif lastaction["action"] == "QUIT":
        irc.msg(target, "{} ({}) was seen quitting {} ({})".format(
            nickObj.nickname, nickObj.prefix, pretty_date(lastaction["time"]), lastaction["args"]))

    elif lastaction["action"] == "KICK":
        irc.msg(target, "{} ({}) was last seen kicked from {} {} ({})".format(
            nickObj.nickname, nickObj.prefix, lastaction["chan"], pretty_date(lastaction["time"]), lastaction["args"]))

    elif lastaction["action"] == "NICK":
        irc.msg(target, "{} ({}) was last seen changing nick to {} {}".format(
            nickObj.nickname, nickObj.prefix, lastaction["args"], pretty_date(lastaction["time"])))
