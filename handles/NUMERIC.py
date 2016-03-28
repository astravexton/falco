import random, time
from utils import parse_modes, getNewNick, chanmodes, check_mask

def handle_001(irc, args):
    #irc.nick = args[1].split()[-1].split("!")[0]
    #irc.user = args[1].split()[-1].split("!")[1].split("@")[0]
    #irc.host = args[1].split()[-1].split("@")[1]
    for chan in irc.channels:
        try:
            if irc.channels[chan]["autojoin"]:
                irc.send("JOIN {}".format(chan))
        except KeyError:
            log.warn("(%s) %s does not have autojoin key, adding autojoin = False", irc.netname, chan)
            irc.channels[chan]["autojoin"] = False
    for chan in irc.autojoin:
        irc.send("JOIN {}".format(chan))

def handle_005(irc, args):

    for arg in args.args:

        if arg.startswith("CHANMODES"):
            chanmodes["*A"],
            chanmodes["*B"],
            chanmodes["*C"],
            chanmodes["*D"] = arg.split("=")[1].split(",")

        if arg.startswith("NICKLEN"):
            irc.nicklen = arg.split("=")[1]

        if arg.startswith("TOPICLEN"):
            irc.topiclen = arg.split("=")[1]

        if arg.startswith("PREFIX"):
            prefix = arg.split("=")[1]
            prefix = re.search(r'\((.*)\)(.*)', prefix)
            irc.prefixmodes = dict(zip(prefix.group(1), prefix.group(2)))
            irc.modesprefix = dict(zip(prefix.group(2), prefix.group(1)))

def handle_251(irc, args):
    irc.send("MODE {} {}".format(irc.nick, irc.setmodes))
    irc.send("WHOIS {}".format(irc.nick))
    #for chan in irc.autojoin:
    #    irc.send("JOIN {}".format(chan))


def handle_265(irc, args):
    # ['falco-devel', '4', '53', 'Current local users 4, max 53']
    #irc.localusers = args.args[1]
    #irc.localmaxusers = args.args[2]
    pass

def handle_266(irc, args):
    # ['falco', '9', '49', 'Current global users 9, max 49']
    #irc.globalusers = args.args[1]
    #irc.globalmaxusers = args.args[2]
    pass

def handle_311(irc, args):
    # ['falco', 'falco', 'falco', 'FCA67DC7.93D0F161.F235D4E8.IP', '*', "nathan's bot"]
    irc.host = args.args[3]

def handle_314(irc, args):
    # ['zero', 'nathan', 'nathan', 'hide-A31D54D.zyr.io', '*', 'nathan']
    nick, ident, host = args.args[1:4]
    if nick not in irc.nicks:
        irc.nicks[nick] = {}
    if "recent" not in irc.nicks[nick]:
        irc.nicks[nick]["recent"] = set()
    irc.nicks[nick]["recent"].add(host)

def handle_324(irc, args):
    # ['falco', '#test', '+ntlk', '2', 'test']
    chan = args.args[1]
    modes = args.args[2:]
    irc.channels[chan]["modes"] = parse_modes(irc, modes)["add"]
    if "extended-join" in irc.cap:
        irc.send("WHO {} %tcuihnar,314".format(chan))
    else:
        irc.send("WHO {}".format(chan))
    # TODO: send WHO differently if connected to charybdis to get account NAMES
    # TODO: parse WHO output depending on the type of server

def handle_332(irc, args):
    # ['nathan', '#programming', 'some topic']
    chan, topic = args.args[1:]
    if chan not in irc.channels:
        irc.channels[chan] = {
            "modes": (),
            "nicks": {},
            "topic": None,
            "buffer": [],
            "autojoin": False
        }
    irc.channels[chan]["topic"] = topic

def handle_352(irc, args):
    # ['falco', '#programming', 'robin', 'hide-FDB00B6A.io', 'mindjail.subluminal.net', 'neoinr', 'H', '0 Robin']
    chan, ident, host, server, nick = args.args[1:6]
    gecos = args.args[7].split(" ",1)[-1]
    if nick not in irc.nicks:
        irc.nicks[nick] = {
            "nick": nick,
            "ident": ident,
            "host": host,
            "gecos": gecos,
            "channels": list(),
            "server": server
        }
    if chan not in irc.nicks[nick]["channels"]:
        irc.nicks[nick]["channels"].append(chan)

def handle_353(irc, args):
    # ['falco', '=', '#test', 'falco @nathan @ChanServ']
    chan, nicks = args.args[2:]
    nicks = nicks.split()

    if chan not in irc.channels:
        irc.channels[chan] = {
            "modes": (),
            "nicks": {},
            "buffer": [],
            "autojoin": False
        }

    for nick in nicks:
        if nick[0] in irc.prefixmodes.values():
            prefix = irc.modesprefix[nick[0]]
            nick = nick[1:]

        else:
            prefix = ""

        irc.channels[chan]["nicks"][nick] = prefix

def handle_354(irc, args):
    # ['falco-devel', '314', '#Zyrio', 'gl', '45.79.66.40', 'millennium.overdrivenetworks.com', 'GLolol', '0', "You can't be serious."]
    tgt, magic, chan, user, realip, host, nick, account, gecos = args.args
    if magic == "314":
        if nick not in irc.nicks:
            irc.nicks[nick] = {
                "nick": nick,
                "ident": user,
                "host": host,
                "gecos": gecos,
                "channels": list(),
                "server": None,
                "account": account
            }
        else:
            irc.nicks[nick]["ident"] = user
            irc.nicks[nick]["host"] = host
            irc.nicks[nick]["gecos"] = gecos
            irc.nicks[nick]["account"] = account
        if chan not in irc.nicks[nick]["channels"]:
            irc.nicks[nick]["channels"].append(chan)

def handle_366(irc, args):
    # ['nathan', '#test', 'End of /NAMES list.']
    chan = args.args[1]
    irc.send("MODE {}".format(chan))

def handle_MODE(irc, args):
    # falco
    # ['+xB']
    # {'add': [], 'rem': [('B', None)]}
    target = args.args[0]
    raw_modes = args.args[1:]
    parsed_modes = parse_modes(irc, raw_modes)

    if target == irc.nick:
        for mode in parsed_modes["add"]:
            irc.modes.append(mode[0])
        for mode in parsed_modes["rem"]:
            irc.modes.remove(mode[0])

    elif target[0] == "#":
        for mode in parsed_modes["add"]:
            if mode[0] not in ["b", "q", "e", "I", "o", "h", "v"]:
                pass
                #irc.channels[target]["modes"].append(mode)
            else:
                if mode[0] in ["o", "v", "h"]:
                    #if irc.channels"][target]["nicks"][mode[1]]
                    irc.channels[target]["nicks"][mode[1]] = mode[0]

        for mode in parsed_modes["rem"]:
            if mode[0] not in ["b", "q", "e", "I", "o", "h", "v"]:
                try:
                    irc.channels[target]["modes"].remove(mode)
                except:
                    pass
            else:
                irc.channels[target]["nicks"][mode[1]] = ""

        if ("o", irc.nick) in parsed_modes["add"]:
            if target in irc.chanmodes:
                if irc.chanmodes[target] != []:
                    for command in irc.chanmodes[target]:
                        irc.send(command)
                    irc.chanmodes[target] = []
                    time.sleep(3)
                    irc.send("MODE {} -o {}".format(target, irc.nick))

def handle_433(irc, args):

    getNewNick(irc, args.args[1])

    if args.args[-1] == "Nickname is already in use.":
        irc.send("NICK {}".format(irc.nick))

def handle_432(irc, args):

    getNewNick(irc, args.args[1])

    if args[-1] == "Erroneous Nickname":
        irc.send("NICK {}".format(irc.nick))
