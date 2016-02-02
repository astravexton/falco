import random, time
from utils import parse_modes, getNewNick, chanmodes, check_mask

def handle_001(irc, source, args):
    # ['nathan', 'Welcome to the Internet Relay Chat Network nathan!weechat@proxy']
    # ['falco', 'Welcome to the subluminal IRC Network falco!falco@213.205.253.114']
    #irc.nick = args[1].split()[-1].split("!")[0]
    #irc.ident = args[1].split()[-1].split("!")[1].split("@")[0]
    irc.host = args[1].split()[-1].split("@")[1]

def handle_005(irc, source, args):

    for arg in args:

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

def handle_251(irc, source, args):
    irc.send("MODE {} {}".format(irc.nick, irc.setmodes))
    irc.send("WHOIS {}".format(irc.nick))
    #for chan in irc.autojoin:
    #    irc.send("JOIN {}".format(chan))


def handle_265(irc, source, args):
    # ['falco', '2', '21', 'Current local users 2, max 21']
    irc.localusers = args[1]
    irc.localmaxusers = args[2]

def handle_266(irc, source, args):
    # ['falco', '9', '49', 'Current global users 9, max 49']
    irc.globalusers = args[1]
    irc.globalmaxusers = args[2]

def handle_311(irc, source, args):
    # ['falco', 'falco', 'falco', 'FCA67DC7.93D0F161.F235D4E8.IP', '*', "nathan's bot"]
    irc.host = args[3]
    if "*!nathan@{}".format(args[3]) not in irc.admins:
        irc.admins.append("*!nathan@{}".format(args[3]))

def handle_314(irc, source, args):
    # ['zero', 'nathan', 'nathan', 'hide-A31D54D.zyr.io', '*', 'nathan']
    nick, ident, host = args[1:4]
    if nick not in irc.nicks:
        irc.nicks[nick] = {}
    if "recent" not in irc.nicks[nick]:
        irc.nicks[nick]["recent"] = set()
    irc.nicks[nick]["recent"].add(host)

def handle_324(irc, source, args):
    # ['falco', '#test', '+ntlk', '2', 'test']
    chan = args[1]
    modes = args[2:]
    irc.channels[chan]["modes"] = parse_modes(irc, modes)["add"]
    irc.send("WHO {}".format(chan))

def handle_332(irc, source, args):
    # ['nathan', '#programming', 'some topic']
    chan, topic = args[1:]
    if chan not in irc.channels:
        irc.channels[chan] = {
            "modes": (),
            "nicks": {},
            "topic": None,
            "buffer": []
        }
    irc.channels[chan]["topic"] = topic

def handle_352(irc, source, args):
    # ['falco', '#programming', 'robin', 'hide-FDB00B6A.io', 'mindjail.subluminal.net', 'neoinr', 'H', '0 Robin']
    chan, ident, host, server, nick = args[1:6]
    gecos = args[7].split(" ",1)[-1]
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

def handle_353(irc, source, args):
    # ['falco', '=', '#test', 'falco @nathan @ChanServ']
    chan, nicks = args[2:]
    nicks = nicks.split()

    if chan not in irc.channels:
        irc.channels[chan] = {
            "modes": (),
            "nicks": {},
            "buffer": []
        }

    for nick in nicks:
        if nick[0] in irc.prefixmodes.values():
            prefix = irc.modesprefix[nick[0]]
            nick = nick[1:]

        else:
            prefix = ""

        irc.channels[chan]["nicks"][nick] = prefix

def handle_366(irc, source, args):
    # ['nathan', '#test', 'End of /NAMES list.']
    chan = args[1]
    irc.send("MODE {}".format(chan))

def handle_KICK(irc, source, args):
    # ['##test', '_', 'my finger slipped']
    if args[1] == irc.nick and irc.netname == "subluminal" and args[0] == "#programming":
        if source.split("!")[0] == "ChanServ":
            n = args[2].split(" ")[0].replace("(","").replace(")", "")
        else:
            n = source.split("!")[0]
        irc.send("PRIVMSG ChanServ :KICK {} {}".format(args[0], n))
        time.sleep(1)
        irc.send("JOIN {}".format(args[0]))

def handle_MODE(irc, source, args):
    # falco
    # ['+xB']
    # {'add': [], 'rem': [('B', None)]}
    target = args[0]
    raw_modes = args[1:]
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

        if target == "#programming" and irc.netname == "subluminal":
            if ("o", irc.nick) in parsed_modes["rem"]:
                irc.send("PRIVMSG ChanServ :OP {}".format(target))
                irc.send("PRIVMSG ChanServ :KICK {} {}".format(target, source.split("!")[0]))
            
            l = [m for m in parsed_modes["add"] if m[0] == "b"]
            for mode, host in l:
                ip = re.split("[./:]", host.split("@")[1])
                for cip in ip:
                    if cip in irc.host or irc.nick in host:
                        irc.send("PRIVMSG ChanServ :UNBAN {}".format(target))
                        irc.send("PRIVMSG ChanServ :KICK {} {}".format(target, source.split("!")[0]))
                        break

            

def handle_433(irc, source, args):

    getNewNick(irc, args[1])

    if args[-1] == "Nickname is already in use.":
        irc.send("NICK {}".format(irc.nick))

def handle_432(irc, source, args):

    getNewNick(irc, args[1])

    if args[-1] == "Erroneous Nickname":
        irc.send("NICK {}".format(irc.nick))
