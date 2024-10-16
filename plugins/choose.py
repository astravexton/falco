import random
from utils import add_regex

def choose(irc, target, args, cmdargs):
    choices = [c.strip() for c in cmdargs[0].split(",")]
    if len(choices) > 1 and choices:
        choice = random.choice(choices).strip()
        if choice:
            irc.send("PRIVMSG {} :{}: {}".format(target, args.sender.nick, choice))
        elif not choice:
            irc.msg(target, "{}: I can't give you any choice".format(args.sender.nick))
    elif len(choices) == 1:
        irc.send("PRIVMSG {} :{}: {}".format(target, args.sender.nick, cmdargs[0]))

add_regex(choose, "^\.choose (.*)")
