from utils import connections, isAdmin, bot_regexes, timesince

def handle_ERROR(irc, args):
    irc.connected = False
    irc.run()

def handle_KILL(irc, args):
    # Closing Link: hostmask (Killed (nathan (test)))
    irc.connected = False
    irc.run() # reconnect on KILL