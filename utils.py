import fnmatch, time, re, glob, os, imp, datetime, requests
from collections import defaultdict
from log import log

global bot_commands, bot_regexes, connections

api_keys = []

def lookup(id):
    params = {
        "part": "id,snippet,contentDetails,statistics,status,liveStreamingDetails",
        "id": id,
        "key": api_keys["youtube"]
    }
    p = requests.get("https://www.googleapis.com/youtube/v3/videos", params=params)
    if p.ok:
        return p.json()

def YTsearch(q):
    params = {
        "q": q,
        "part": "id",
        "maxResults": 1,
        "type": "video",
        "key": api_keys["youtube"]
    }
    p = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
    if p.ok:
        ids = []
        for video in p.json()["items"]:
            ids.append(video["id"]["videoId"])
        return lookup(",".join(ids))

plugins = []
bot_commands = {}
bot_regexes = {}
command_hooks = defaultdict(list)
connections = dict()
mtimes = {}

def isSelfOp(irc, target):
    if irc.channels[target]["nicks"][irc.nick] == "o":
        return True
    return False 

def doOpStuff(irc, target):
    if irc.chanmodes[target] != []:
        for command in irc.chanmodes[target]:
            irc.send(command)
        irc.chanmodes[target] = []

class Address(object):
    def __init__(self, addr):
        self.nick, self.ident, self.mask = (
            addr[:addr.find("!")][1:],
            addr.split("@")[0][addr.find("!")+1:],
            addr.split("@")[1]
           )
        self.hostmask = addr.replace(":", "", 1)


class parseArgs(object):   
    def __init__(self, args):
        args = args.split(" ")
        real_args = []
        for idx, arg in enumerate(args):
            real_args.append(arg)
            if arg.startswith(':') and idx != 0:
                arg = args[idx:]
                arg = ' '.join(arg)[1:]
                real_args = args[:idx]
                real_args.append(arg)
                break
        if "@" not in real_args[0]:
            self.sender = real_args[0]
        else:
            self.sender = Address(real_args[0])
        self.type = real_args[1]
        self.args = real_args[2:]
        if not args[0].startswith(":"):
            self.sender = None
            self.type, self.args = real_args[0:]

def shorten(url, custom=None, key=None):
    p = {'url': url, 'shorturl': custom, 'format': 'json'}
    r = requests.get('http://is.gd/create.php', params=p)
    j = r.json()
    if 'shorturl' in j:
        return j['shorturl']
    else:
        raise url

def expand(url):
    p = {'shorturl': url, 'format': 'json'}
    r = requests.get('http://is.gd/forward.php', params=p)
    j = r.json()
    if 'url' in j:
        return j['url']
    else:
        return url

time_expression = r"((?:(?:\d+|\ban?\b)\s*(?:[wdhms]|(?:sec|min|second|minute|hour|day|week|wk|hr)s?)\s*)+)"

seconds_map = {"w": 604800,
               "wk": 604800,
               "week": 604800,
               "d": 24 * 60 * 60,
               "day": 24 * 60 * 60,
               "h": 60 * 60,
               "hr": 60 * 60,
               "hour": 60 * 60,
               "m": 60,
               "min": 60,
               "minute": 60,
               "": 1,
               "sec": 1,
               "second": 1}

def parse_time(expr):
    if not expr:
        return 0
    tokens = re.split(r"(\d+|\ban?\b)", expr)
    tokens = tokens[1:]
    tokens = [i.strip() for i in tokens]
    units = zip(tokens[::2], tokens[1::2])
    seconds = 0
    for num, unit in units:
        if num.isdigit():
            num = int(num)
        else:
            num = 1
        seconds += num * seconds_map[unit.rstrip("s").lower()]
    return seconds

def from_now(seconds):
    units = ["seconds", "minutes", "hours", "days", "weeks", "years"]
    multipliers = [60, 60, 24, 7, 52.14]
    acc = []
    qty = seconds
    for i in multipliers:
        qty, unit = divmod(qty, i)
        acc.append(unit)
    acc.append(qty)
    return " ".join(["%d %s" % (q, u) for q, u in zip(acc, units) if q][::-1])


def decode(txt):
    for codec in ('utf-8', 'iso-8859-1', 'shift_jis', 'cp1252'):
        try:
            return txt.decode(codec)

        except UnicodeDecodeError:
            continue

    return txt.decode('utf-8', 'ignore')

def add_cmd(func, name=None):
    """ add_cmd(func name=None) """
    if name is None:
        name = func.__name__

    name = name
    bot_commands[name] = func
    #print("Added command {} as {}".format(func, name))

def add_regex(func, regex=None):
    if regex == None:
        log.warn("Unable to add regex for %s", func.__name__)
    else:
        bot_regexes[re.compile(regex)] = func
        log.debug("Added regex %s for %s", regex, func.__name__)

def add_hook(func, command):
    """Add a hook <func> for command <command>."""
    command = command.upper()
    command_hooks[command].append(func)

chanmodes = {'op': 'o', 'voice': 'v', 'ban': 'b', 'key': 'k', 'limit':
             'l', 'moderated': 'm', 'noextmsg': 'n', 'noknock': 'p',
             'secret': 's', 'topiclock': 't',
             'quiet': 'q', 'redirect': 'f', 'freetarget': 'F',
             'joinflood': 'j', 'largebanlist': 'L', 'permanent': 'P',
             'c_noforwards': 'Q', 'stripcolor': 'c', 'allowinvite':
             'g', 'opmoderated': 'z', 'noctcp': 'C', 'regonly': 'r',
            'invex': 'I', 'banexception': 'e',
             '*A': 'beI', '*B': 'k', '*C': 'l', '*D': 'mnprst'}

umodes = {'deaf': 'D', 'servprotect': 'S', 'u_admin': 'a',
          'invisible': 'i', 'oper': 'o', 'wallops': 'w',
          'snomask': 's', 'u_noforward': 'Q', 'regdeaf': 'R',
          'callerid': 'g', 'chary_operwall': 'z', 'chary_locops': 'l',
          '*A': '', '*B': '', '*C': '', '*D': 'DSAiowQRglszZ'}

def parse_modes(irc, modes):
    prefixmodes = irc.prefixmodes
    prefix = ""
    res = []
    add, rem = [], []
    args = modes[1:]

    for mode in modes[0]:
        if mode in "+-":
            prefix = mode

        else:
            #print('Current mode: {}{}; args left: {}'.format(prefix, mode, args))
            arg = None
            try:
                if mode in (chanmodes['*A'] + chanmodes['*B']):
                    #print('Mode {}: This mode must have parameter.'.format(mode))
                    arg = args.pop(0)

                    if prefix == '-' and mode in chanmodes['*B'] and arg == '*':
                        oldargs = [m[1] for m in arg if m[0] == mode]

                        if oldargs:
                            arg = oldargs[0]
                            #log.debug("Mode %s: coersing argument of '*' to %r.", mode, arg)

                elif mode in prefixmodes.keys():
                    #print('Mode {}: This mode is a prefix mode.'.format(mode))
                    arg = args.pop(0)

                elif prefix == '+' and mode in chanmodes['*C']:
                    #print('Mode {}: Only has parameter when setting.'.format(mode))
                    arg = args.pop(0)

            except IndexError:
                continue

            if prefix == "-":
                rem.append((mode, arg))
            elif prefix == "+":
                add.append((mode, arg))

    return {"add": add, "rem": rem}

def isAdmin(irc, user):
    for admin in irc.admins["hosts"]:
        if fnmatch.fnmatch(user.hostmask, admin):
            return True
    try:
        account = irc.nicks[user.nick]["account"]
        if account in irc.admins["accounts"]:
            return True
    except:
        return False

    return False

def isOp(irc, user):
    for admin in irc.admins:
        if fnmatch.fnmatch(user.hostmask, admin):
            return True
    for ops in irc.ops:
        if fnmatch.fnmatch(user.hostmask, ops):
            return True
    try:
        return True if user.nick in irc.channels["##chat-bridge"]["nicks"] else False
    except:
        return False

def getNewNick(irc, nick=None, new=True):
    if not nick:
        nick = irc.nick

    irc.oldnick = irc.nick
    irc.nick = irc.oldnick+"_"

    irc.send("NICK {}".format(irc.nick))

import datetime


def timesince(d, now=None):
    chunks = (
      #(60 * 60 * 24 * 365, ('year', 'years')),
      (60 * 60 * 24 * 30, ('month', 'months')),
      #(60 * 60 * 24 * 7, ('week', 'weeks')),
      (60 * 60 * 24, ('day', 'days')),
      (60 * 60, ('hour', 'hours')),
      (60, ('minute', 'minutes'))
    )

    # Convert int or float (unix epoch) to datetime.datetime for comparison
    if isinstance(d, int) or isinstance(d, float):
        d = datetime.datetime.fromtimestamp(d)

    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now()

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return u'0 ' + 'minutes'
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break

    if count == 1:
        s = '%(number)d %(type)s' % {'number': count, 'type': name[0]}
    else:
        s = '%(number)d %(type)s' % {'number': count, 'type': name[1]}

    if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            if count2 == 1:
                s += ', %d %s' % (count2, name2[0])
            else:
                s += ' and %d %s' % (count2, name2[1])
    return s


def timeuntil(d, now=None):
    if not now:
        now = datetime.datetime.now()
    return timesince(now, d)

def check_mask(irc, ip):
    l = list(zip(re.split("[./:]", irc.host), re.split("[./:]", ip)))
    for idx, tup in enumerate(l[::]):
        l[idx] = set(tup)

    if len(set.union(*l)) == len(re.split("[./:]", irc.host)): return True
    else: return False

