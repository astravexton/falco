import base64, time, sys

def handle_CAP(irc, args):
    if args.args[1] == "ACK":
        irc.send("AUTHENTICATE PLAIN")

def handle_AUTHENTICATE(irc, args):
    if args.args[0] == "+":
        stuff = "{0}\0{0}\0{1}".format(irc.conf["sasl_username"],irc.conf["sasl_password"])
        irc.send("AUTHENTICATE {}".format(base64.b64encode(stuff.encode()).decode()))

def handle_903(irc, args):
    irc.send("CAP END")

def handle_904(irc, args):
    sys.exit(1)

def handle_905(irc, args):
    sys.exit(1)

