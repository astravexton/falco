import random, time
from utils import parse_modes, getNewNick, chanmodes, check_mask, User
from log import log
import re

def handle_001(irc, args):
    #irc.nick = args[1].split()[-1].split("!")[0]
    #irc.user = args[1].split()[-1].split("!")[1].split("@")[0]
    #irc.host = args[1].split()[-1].split("@")[1]
    #self.netname = args.args[1].split(" ")[3]
    log.info("(%s) Connected as %s", irc.netname, irc.nick)
    for chan in irc.channels:
        try:
            if irc.channels[chan]["autojoin"]:
                irc.send("JOIN {}".format(chan))
        except KeyError:
            log.warn("(%s) %s does not have autojoin key, adding autojoin = False", irc.netname, chan)
            irc.channels[chan]["autojoin"] = False
    for chan in irc.autojoin:
        irc.send("JOIN {}".format(chan))

def handle_002(irc, args):
    irc.nethost = args.args[1].split(" ")[3][:-1]

def handle_005(irc, args):

    for arg in args.args:

        if arg.startswith("CHANMODES"):
            chanmodes.update({k:v for k,v in zip(['*A','*B','*C','*D'], arg.split("=")[1].split(","))})

        if arg.startswith("NICKLEN"):
            irc.nicklen = int(arg.split("=")[1])

        if arg.startswith("TOPICLEN"):
            irc.topiclen = int(arg.split("=")[1])

        if arg.startswith("PREFIX"):
            prefix = arg.split("=")[1]
            prefix = re.search(r'\((.*)\)(.*)', prefix)
            irc.prefixmodes = dict(zip(prefix.group(1), prefix.group(2)))
            irc.modesprefix = dict(zip(prefix.group(2), prefix.group(1)))

        if arg.startswith("NETWORK"):
            irc.network = arg.split("=")[1]

def handle_251(irc, args):
    # ['falco-dev', 'There are 1 users and 1 invisible on 1 servers']
    irc.send("MODE {} {}".format(irc.nick, irc.setmodes))
    irc.send("WHOIS {}".format(irc.nick))
    # for chan in irc.autojoin:
    #    irc.send("JOIN {}".format(chan))

def handle_311(irc, args):
    # ['falco', 'falco', 'falco', 'FCA67DC7.93D0F161.F235D4E8.IP', '*', "nathan's bot"]
    if args.args[0] == args.args[1]:
        irc.host = args.args[3]


def handle_324(irc, args):
    # ['falco', '#test', '+ntlk', '2', 'test']
    chan = args.args[1]
    modes = args.args[2:]
    chanObj = irc.get_channel(chan)
    chanObj.modes = parse_modes(irc, modes)["add"]
    # irc.channels[chan]["modes"] = parse_modes(irc, modes)["add"]

def handle_332(irc, args):
    # ['nathan', '#programming', 'some topic']
    chan, topic = args.args[1:]
    chanObj = irc.get_channel(chan)
    chanObj.topic = topic
    # if chan not in irc.channels:
    #     irc.channels[chan] = {
    #         "modes": (),
    #         "nicks": {},
    #         "topic": None,
    #         "buffer": [],
    #         "autojoin": False
    #     }
    # irc.channels[chan]["topic"] = topic

def handle_346(irc, args):
    # ['falco-dev', '#dev', 'moo!*@*', 'astra', '1485310321']
    chan, mode = args.args[1:3]
    chanObj = irc.get_channel(chan)
    chanObj.invexs.append(mode)

def handle_348(irc, args):
    # ['falco-dev', '#dev', 'aksdosa!*@*', 'astra', '1485310323']
    chan, mode = args.args[1:3]
    chanObj = irc.get_channel(chan)
    chanObj.excepts.append(mode)

def handle_352(irc, args):
    # ['falco', '#programming', 'robin', 'hide-FDB00B6A.io', 'mindjail.subluminal.net', 'neoinr', 'H', '0 Robin']
    chan, ident, host, server, nick = args.args[1:6]
    gecos = args.args[7].split(" ",1)[-1]
    chanObj = irc.get_channel(chan)
    userObj = irc.get_user(nick)
    if userObj.host == "":
        userObj.host = host
        userObj.user = ident
        userObj.gecos = gecos
        userObj.nickname = nick
    irc.users[nick] = userObj
    chanObj.add_member(nick, userObj)
    userObj.channels[chan] = chanObj
    # if nick not in irc.nicks:
    #     irc.nicks[nick] = {
    #         "nick": nick,
    #         "ident": ident,
    #         "host": host,
    #         "gecos": gecos,
    #         "channels": list(),
    #         "server": server
    #     }
    # if chan not in irc.nicks[nick]["channels"]:
    #     irc.nicks[nick]["channels"].append(chan)

def handle_353(irc, args):
    # ['falco', '=', '#test', 'falco @nathan @ChanServ']
    chan, nicks = args.args[2:]
    nicks = nicks.split()
    chanObj = irc.get_channel(chan)
    for nick in nicks:
        if nick[0] in irc.prefixmodes.values():
            prefix = irc.modesprefix[nick[0]]
            nick = nick[1:]
        else:
            prefix = ""
        chanObj.usermodes[nick] = prefix

def handle_354(irc, args):
    # ['falco-devel', '314', '#Zyrio', 'gl', '45.79.66.40', 'millennium.overdrivenetworks.com', 'GLolol', '0', "You can't be serious."]
    _, magic, chan, user, realip, host, nick, account, gecos = args.args
    if magic == "314":
        chanObj = irc.get_channel(chan)
        userObj = irc.get_user(nick)
        if userObj.host == "":
            userObj.host = host
            userObj.user = user
            userObj.gecos = gecos
            userObj.nickname = nick
            userObj.account =  account
        irc.users[nick] = userObj
        chanObj.add_member(nick, userObj)
        userObj.channels[chan] = chanObj
        # if nick not in irc.nicks:
        #     irc.nicks[nick] = {
        #         "nick": nick,
        #         "ident": user,
        #         "host": host,
        #         "gecos": gecos,
        #         "channels": list(),
        #         "server": None,
        #         "account": account
        #     }
        # else:
        #     irc.nicks[nick]["ident"] = user
        #     irc.nicks[nick]["host"] = host
        #     irc.nicks[nick]["gecos"] = gecos
        #     irc.nicks[nick]["account"] = account
        # if chan not in irc.nicks[nick]["channels"]:
        #     irc.nicks[nick]["channels"].append(chan)

def handle_366(irc, args):
    # ['nathan', '#test', 'End of /NAMES list.']
    chan = args.args[1]
    # irc.send("MODE {}".format(chan))
    for mode in list(chanmodes["*A"]):
        irc.send("MODE {} {}".format(chan, mode))
    if "extended-join" in irc.cap:
        irc.send("WHO {} %tcuihnar,314".format(chan))
    else:
        irc.send("WHO {}".format(chan))
    # TODO: send WHO differently if connected to charybdis to get account NAMES
    # TODO: parse WHO output depending on the type of server

def handle_367(irc, args):
    # ['falco-dev', '#dev', 'test!*@*', 'astra', '1485309813']
    chan, mode = args.args[1:3]
    chanObj = irc.get_channel(chan)
    chanObj.bans.append(mode)


def handle_396(irc, args):
    irc.host = args.args[1]

def handle_433(irc, args):

    getNewNick(irc, args.args[1])
    if args.args == "Nickname is registered to someone else":
        irc.send("PRIVMSG NickServ :identify {}".format(irc.conf.get("nickserv_password")))

    elif args.args[-1] == "Nickname is already in use.":
        irc.send("NICK {}".format(irc.nick))

def handle_432(irc, args):

    getNewNick(irc, args.args[1])

    if args.args[-1] == "Erroneous Nickname":
        irc.send("NICK {}".format(irc.nick))
