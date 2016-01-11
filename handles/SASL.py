import base64, time, sys

def handle_CAP(irc, source, args):
    if args[1] == "ACK":
        irc.send("AUTHENTICATE PLAIN")

def handle_AUTHENTICATE(irc, source, args):
    if args[1] == "+":
        stuff = "{0}\0{0}\0{1}".format(irc.conf["sasl_username"],irc.conf["sasl_password"])
        irc.send("AUTHENTICATE {}".format(base64.b64encode(stuff.encode()).decode()))

def handle_903(irc, source, args):
    irc.send("CAP END")

def handle_904(irc, source, args):
    sys.exit(1)

def handle_905(irc, source, args):
    sys.exit(1)


