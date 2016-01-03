from utils import *
import time

def main(irc):
    irc.countdown = 1451044800

@add_cmd
def countdown(irc, source, msgtarget, args):
    if isAdmin(irc, source):
        while True:
            days = int((irc.countdown - int(time.time())) / (3600*24))
            irc.send("TOPIC {} :{}".format(msgtarget, irc.channels[msgtarget]["topic"].replace(str(days+1), str(days))))
            time.sleep(3600*24)
