import fnmatch, time, re, glob, os, imp, datetime, requests
from collections import defaultdict
from log import log

global bot_commands, bot_regexes, connections, user_hooks, command_hooks

user_hooks = {}

api_keys = []

def bot_version():
    pipe = os.popen("git log --oneline")
    output = pipe.read().split("\n")
    pipe.close()
    count = len(output)
    ver = output[0].split(" ")[0]
    return "%s-%d" % (ver, count)

class User:
    def __init__(self, server, nickname, user, host, gecos=None, account=None):
        self.nickname = nickname
        self.user = user
        self.host = host
        self.gecos = gecos
        self.account = account
        self.channels = {}
        self.lastaction = {"action": "", "args": None, "time": 0, "chan": None}
        self.ignored = False
        self.reminders = []

    @property
    def prefix(self):
        return "%s!%s@%s" % (self.nickname, self.user, self.host)

    def remove_channel(self, channel):
        del self.channels[channel]

class Channel:
    def __init__(self, server, name):
        self.server = server
        self.name = name
        self.members = {}
        self._topic = ""
        self.oldtopics = []
        self.key = None
        self.modes = []
        self.usermodes = {}
        self.bans = []
        self.quiets = []
        self.invexs = []
        self.excepts = []
        self.buffer = []

    def add_member(self, nickname, user):
        self.members[nickname] = user

    @property
    def topic(self):
        return self._topic

    @topic.setter
    def topic(self, value):
        self._topic = value

    def append_old_topic(self, value):
        self.oldtopics.insert(0, value)
        if len(self.oldtopics) >= 25:
            self.oldtopics.pop(-1)

    def remove_member(self, client):
        if client.nickname in self.members.keys():
            del self.members[client.nickname]

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
            self.sender = Address("*!*@"+real_args[0].lstrip(":"))
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
    log.debug("Added command %r for %r", name, func.__name__)

def add_regex(func, regex=None):
    if regex == None:
        log.warn("Unable to add regex for %r", func.__name__)
    else:
        bot_regexes[re.compile(regex)] = func
        log.debug("Added regex %r for %r", regex, func.__name__)

def add_hook(func, command):
    """Add a hook <func> for command <command>."""
    if type(command) == list:
        for c in command:
            command = c.upper()
            command_hooks[command].append(func)
            log.debug("Added hook %r on %r" % (func.__name__, command))
    else:
        command_hooks[command].append(func)
        log.debug("Added hook %r on %r" % (func.__name__, command))

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
        userObj = irc.get_user(user.nick)
        if userObj.account in irc.admins["accounts"]:
            return True
    except:
        return False

    return False

def isOp(irc, user):
    for admin in irc.admins["hosts"]:
        if fnmatch.fnmatch(user.hostmask, admin):
            return True
    try:
        userObj = irc.get_user(user.nick)
        if userObj.account in irc.ops["accounts"]:
            return True
    except:
        return False

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

def overline(text):
    return "\u0305" + "\u0305".join(text)


def strikethrough(text):
    text = re.split(
        r"(\x03(?:\d{0,2}(?:,\d{1,2})?)?|\x1f|\x0f|\x16|\x02|\u0305)",
        text
    )
    # Replace odd indices with strikethrough'd versions
    text = [
        t if i % 2 else "\u0336" + "\u0336".join(t) for i, t in enumerate(text)
    ]
    return "".join(text)


def underline(text):
    return "\u0332" + "\u0332".join(text)


def smallcaps(text):
    # TODO: Move into config
    caps = {
        'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ',
        'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ', 'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ',
        'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ'
    }
    return "".join(caps.get(i, i) for i in text)


def fullwidth(text):
    full = {
        '|': '｜', '~': '～', 'x': 'ｘ', 'z': 'ｚ', 't': 'ｔ', 'v': 'ｖ',
        'p': 'ｐ', 'r': 'ｒ', 'l': 'ｌ', 'n': 'ｎ', 'h': 'ｈ', 'j': 'ｊ',
        'd': 'ｄ', 'f': 'ｆ', '`': '｀', 'b': 'ｂ', '\\': '＼', '^': '＾',
        'X': 'Ｘ', 'Z': 'Ｚ', 'T': 'Ｔ', 'V': 'Ｖ', 'P': 'Ｐ', 'R': 'Ｒ',
        'L': 'Ｌ', 'N': 'Ｎ', 'H': 'Ｈ', 'J': 'Ｊ', 'D': 'Ｄ', 'F': 'Ｆ',
        '@': '＠', 'B': 'Ｂ', '<': '＜', '>': '＞', '8': '８', ':': '：',
        '4': '４', '6': '６', '0': '０', '2': '２', ',': '，', '.': '．',
        '(': '（', '*': '＊', '$': '＄', '&': '＆', '"': '＂', '}': '｝',
        'y': 'ｙ', '{': '｛', 'u': 'ｕ', 'w': 'ｗ', 'q': 'ｑ', 's': 'ｓ',
        'm': 'ｍ', 'o': 'ｏ', 'i': 'ｉ', 'k': 'ｋ', 'e': 'ｅ', 'g': 'ｇ',
        'a': 'ａ', 'c': 'ｃ', ']': '］', '_': '＿', 'Y': 'Ｙ', '[': '［',
        'U': 'Ｕ', 'W': 'Ｗ', 'Q': 'Ｑ', 'S': 'Ｓ', 'M': 'Ｍ', 'O': 'Ｏ',
        'I': 'Ｉ', 'K': 'Ｋ', 'E': 'Ｅ', 'G': 'Ｇ', 'A': 'Ａ', 'C': 'Ｃ',
        '=': '＝', '?': '？', '9': '９', ';': '；', '5': '５', '7': '７',
        '1': '１', '3': '３', '-': '－', '/': '／', ')': '）', '+': '＋',
        '%': '％', "'": '＇', '!': '！', '#': '＃'
    }
    return "".join(full.get(i, i) for i in text)

def pretty_date(delta):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    delta = (time.time() - delta)
    diff = datetime.timedelta(seconds=delta)
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return 'just now'

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(int(second_diff)) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"