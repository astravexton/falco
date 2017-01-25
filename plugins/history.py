import re
import time
from utils import add_cmd, timesince

@add_cmd
def history(irc, source, msgtarget, args):
    c = 0
    if type(args) == int:
        count = int(args)
    else:
        count = 20
    data = []
    chanObj = irc.get_channel(msgtarget)
    for line in chanObj.buffer[-count:]:
        if c < int(count):
            irc.msg(source.nick, line[1])
            c +=1
        else:
            break