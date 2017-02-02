def handle_ACCOUNT(irc, args):
    account = args.args
    nick = args.sender.nick
    irc.nicks[nick]["account"] = account[0]
