from utils import parse_modes, doOpStuff

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
                doOpStuff(irc, target)
                time.sleep(3)
                irc.send("MODE {} -o {}".format(target, irc.nick))
