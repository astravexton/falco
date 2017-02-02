from utils import add_cmd, add_regex
from hashlib import md5
from os import urandom
import time

time_expression = r"((?:(?:\d+|\ban?\b)\s*(?:[wdhms]|(?:sec|min|second|minute|hour|day|week|wk|hr)s?)\s*)+)"
tell_regex = r"^\.(remind|tell)(\s-f)?\s(?:to\s+)?(\S+):?\s+(?:(?:in|after)\s+%(time)s\s+)?(?:that|to\s+)?(what to \S+|.+?)(?:\s+(?:in|after)\s+%(time)s)?(?:\s+via\s+(pm|channel message|message|private message|#\S+))?$" % {"time": time_expression}

def tell(irc, target, args, cmdargs):
    # ('tell', ' -f', 'astra', None, 'test', None, None)
    _, force, to_tell, _, message, delay, via = cmdargs

    if to_tell in ["me", "self"]:
        to_tell = args.sender.nick
    to_tell = to_tell.lstrip("@")

    userObj = irc.get_user(to_tell)

    if userObj.lastaction["time"] != 0:
        if not delay:
            msghash = md5(urandom(20)).hexdigest()[:6]
            userObj.reminders.append((msghash, args.sender.hostmask, message, via if via else "channel", time.time(), target))
            irc.msg(target, "I'll tell them that when they are next active, to delete type \x02.deltell %s %s\x02" % (to_tell, msghash))
    else:
        irc.msg(target, "I've not seen that user before so can't send them a message")

add_regex(tell, tell_regex)

@add_cmd
def deltell(irc, target, args, cmdargs):
    user, msghash = cmdargs.split(" ")
    userObj = irc.get_user(user)
    for reminder in userObj.reminders:
        if reminder[0] == msghash and reminder[1] == args.sender.hostmask:
            userObj.reminders.remove(reminder)
            irc.msg(target, "Reminder %r deleted" % msghash)