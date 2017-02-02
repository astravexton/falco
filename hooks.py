import utils
from handles import *

def check_reminders(irc, args):
    nick = args.sender.nick
    if args.type == "NICK":
        nick = args.args[0]
    userObj = irc.get_user(nick)
    if userObj.reminders == []:
        return

    for reminder in userObj.reminders:
        if reminder[3] in ["channel"]:
            to = reminder[5]
        elif reminder[3] in ["pm", "private message"]:
            to = userObj.nickname

        irc.msg(to, "✉ │ %s: %s · from %s · ⌚ %s ago" %
            (userObj.nickname, reminder[2], reminder[1].split("!")[0], utils.timesince(reminder[4])))

        userObj.reminders.remove(reminder)

def main():
    utils.add_hook(check_reminders, ["JOIN", "NICK", "PRIVMSG", "NOTICE"])
    utils.add_hook(PRIVMSG.handle_NOTICE, ["NOTICE", "PRIVMSG"])
    utils.add_hook(NUMERIC.handle_001, "001")
    utils.add_hook(NUMERIC.handle_002, "002")
    utils.add_hook(NUMERIC.handle_005, "005")
    utils.add_hook(NUMERIC.handle_251, "251")
    utils.add_hook(NUMERIC.handle_311, "311")
    utils.add_hook(NUMERIC.handle_324, "324")
    utils.add_hook(NUMERIC.handle_332, "332")
    utils.add_hook(NUMERIC.handle_346, "346")
    utils.add_hook(NUMERIC.handle_348, "348")
    utils.add_hook(NUMERIC.handle_352, "352")
    utils.add_hook(NUMERIC.handle_353, "353")
    utils.add_hook(NUMERIC.handle_354, "354")
    utils.add_hook(NUMERIC.handle_366, "366")
    utils.add_hook(NUMERIC.handle_367, "367")
    utils.add_hook(NUMERIC.handle_396, "396")
    utils.add_hook(NUMERIC.handle_432, "432")
    utils.add_hook(NUMERIC.handle_433, "433")
    utils.add_hook(ACCOUNT.handle_ACCOUNT, "ACCOUNT")
    utils.add_hook(ERROR.handle_ERROR, ["ERROR", "KILL"])
    utils.add_hook(INVITE.handle_INVITE, "INVITE")
    utils.add_hook(JOIN.handle_JOIN, "JOIN")
    utils.add_hook(KICK.handle_KICK, "KICK")
    utils.add_hook(MODE.handle_MODE, "MODE")
    utils.add_hook(NICK.handle_NICK, "NICK")
    utils.add_hook(PART.handle_PART, "PART")
    utils.add_hook(PING.handle_PING, "PING")
    utils.add_hook(QUIT.handle_QUIT, "QUIT")
    utils.add_hook(SASL.handle_CAP, "CAP")
    utils.add_hook(SASL.handle_AUTHENTICATE, "AUTHENTICATE")
    utils.add_hook(SASL.handle_903, "903")
    utils.add_hook(SASL.handle_904, ["904, 905"])
    utils.add_hook(SASL.handle_905, "905")
    utils.add_hook(TOPIC.handle_TOPIC, "TOPIC")
