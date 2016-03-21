import utils

def handle_INVITE(irc, args):
    if utils.isAdmin(irc, args.sender.hostmask):
        irc.send("JOIN {}".format(args.args[1]))