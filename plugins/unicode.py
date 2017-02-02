from utils import add_cmd
import unicodedata
import sys
import re

@add_cmd
def unicode(irc, target, args, cmdargs):
    unicode_names = []
    for ix in range(sys.maxunicode+1):
        try:
            unicode_names.append((ix, unicodedata.name(chr(ix))))
        except ValueError:
            pass
    pat = re.compile(cmdargs, re.I)
    matches = [(y,x) for (x,y) in unicode_names
                if pat.search(y) is not None]
    if matches:
        output = []
        for match in matches[:125]:
            output.append(chr(match[1]))
        irc.msg(target, " ".join(output))
    else:
        irc.msg(target, "No unicode found.")