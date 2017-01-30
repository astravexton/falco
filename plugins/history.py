import re
import time
from utils import add_cmd, timesince

@add_cmd
def history(irc, target, args, cmdargs):
    c = 0
    if type(cmdargs) == int:
        count = int(cmdargs)
    else:
        count = 20
    data = []
    chanObj = irc.get_channel(target)
    for line in chanObj.buffer[-count:]:
        if c < count:
            irc.msg(args.sender.nick, "%s ago %s" % (timesince(line[0]), line[1]))
            c +=1
        else:
            break