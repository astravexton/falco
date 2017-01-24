from utils import add_cmd
import unicodedata
import sys
import re

@add_cmd
def unicode(irc, source, msgtarget, args):
    unicode_names = []
    for ix in range(sys.maxunicode+1):
        try:
            unicode_names.append((ix, unicodedata.name(chr(ix))))
        except ValueError:
            pass
    pat = re.compile(args, re.I)
    matches = [(y,x) for (x,y) in unicode_names
                if pat.search(y) is not None]
    if matches:
        output = []
        for match in matches[0:70]:
            output.append(chr(match[1]))
        irc.msg(msgtarget, " ".join(output))
    else:
        irc.msg(msgtarget, "No unicode found.")