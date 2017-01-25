from utils import parse_modes, doOpStuff, chanmodes

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
        chanObj = irc.get_channel(target)
        for mode in parsed_modes["add"]:
            if mode[0] in chanmodes["*D"]:
                chanObj.modes.append(mode)
            elif mode[0] in irc.prefixmodes.keys():
                chanObj.usermodes[mode[1]] = mode[0]
            elif mode[0] in chanmodes["*A"] + chanmodes["*B"]:
                if mode[0] == "b": # ban
                    chanObj.bans.append(mode[1])
                elif mode[0] == "q": # quiet
                    chanObj.quiets.append(mode[1])
                elif mode[0] == "I": # invexs
                    chanObj.invexs.append(mode[1])
                elif mode[0] == "E": # excepts
                    chanObj.excepts.append(mode[1])
                else:
                    chanObj.chanmodes.append(mode[1])
            else:
                log.warn("(%s) mode not tracked: +%s %s", irc.netname, mode[0], mode[1])

        for mode in parsed_modes["rem"]:
            if mode[0] in chanmodes["*D"]:
                chanObj.modes.remove(mode)
            elif mode[0] in irc.prefixmodes.keys():
                chanObj.usermodes[mode[1]] = ""
            elif mode[0] in chanmodes["*A"] + chanmodes["*B"]:
                if mode[0] == "b": # ban
                    chanObj.bans.remove(mode[1])
                elif mode[0] == "q": # quiet
                    chanObj.quiets.remove(mode[1])
                elif mode[0] == "I": # invexs
                    chanObj.invexs.remove(mode[1])
                elif mode[0] == "E": # excepts
                    chanObj.excepts.remove(mode[1])
                else:
                    chanObj.chanmodes.remove(mode[1])
            else:
                log.warn("(%s) mode not tracked: -%s %s", irc.netname, mode[0], mode[1])

        if ("o", irc.nick) in parsed_modes["add"]:
            if target in irc.chanmodes:
                doOpStuff(irc, target)
                if irc.channels[target]["autodeop"]:
                    time.sleep(3)
                    irc.send("MODE {} -o {}".format(target, irc.nick))
