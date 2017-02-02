import time

def handle_NICK(irc, args):
    # source: nathan!nathan@392D2D96.A2275890.DCE72A8F.IP
    # args: ['nathanaan']

    oldnick = args.sender.nick
    newnick = args.args[0]

    if oldnick == irc.nick: # if bot changes nick, keep track of it
        irc.nick = newnick

    olduserObj = irc.get_user(oldnick)
    newuserObj = irc.get_user(newnick)
    newuserObj.__dict__ = olduserObj.__dict__.copy()
    irc.users[newnick] = newuserObj
    irc.users[newnick].nickname = newnick
    for chan in newuserObj.channels.values():
        chan.remove_member(olduserObj)
        chan.add_member(newnick, newuserObj)
    olduserObj.lastaction = {"action": "NICK", "args": newnick, "time": time.time(), "chan": None}
