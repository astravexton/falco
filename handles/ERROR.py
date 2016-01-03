from utils import connections, isAdmin, bot_regexes, timesince

def handle_ERROR(irc, source, args):
    print(source, args)
