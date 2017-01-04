import utils

def handle_INVITE(irc, args):
    if utils.isAdmin(irc, args.sender):
        if args.args[1] in irc.autojoin:
            irc.send("JOIN {}".format(args.args[1]))