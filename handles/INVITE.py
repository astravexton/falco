import utils

def handle_INVITE(irc, user, args):
    if utils.isAdmin(irc, user):
        irc.send("JOIN {}".format(args[1]))