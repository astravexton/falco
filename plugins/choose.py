import random
from utils import add_regex

def choose(irc, source, msgtarget, args):
    choices = [c.strip() for c in args[0].split(",")]
    if len(choices) > 1 and choices:
        choice = random.choice(choices).strip()
        if choice:
            irc.send("PRIVMSG {} :{}: {}".format(msgtarget, source.nick, choice))
        elif not choice:
            irc.msg(msgtarget, "{}: I can't give you any choice".format(source.nick))
    elif len(choices) == 1:
        irc.send("PRIVMSG {} :{}: {}".format(msgtarget, source.nick, args[0]))

add_regex(choose, "^\.choose (.*)")