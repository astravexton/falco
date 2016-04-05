import base64, time, sys

def handle_CAP(irc, args):
    # ['*', 'LS', 'account-notify extended-join identify-msg multi-prefix sasl']
    if irc.capdone == False:
        if args.args[1] == "LS":
            caps = args.args[2].split(" ")
            if "extended-join" in caps:
                irc.cap.append("extended-join")
            if irc.conf.get("sasl"):
                irc.cap.append("sasl")
            if irc.cap:
                irc.send("CAP REQ :{}".format(" ".join(irc.cap)))
            if not irc.cap:
                irc.send("CAP END")

        elif args.args[1] == "ACK":
            if irc.conf.get("sasl"):
                irc.send("AUTHENTICATE PLAIN")
            else:
                irc.send("CAP END")
                irc.capdone = True

def handle_AUTHENTICATE(irc, args):
    if args.args[0] == "+":
        stuff = "{0}\0{0}\0{1}".format(irc.conf["sasl_username"],irc.conf["sasl_password"])
        irc.send("AUTHENTICATE {}".format(base64.b64encode(stuff.encode()).decode()))

def handle_900(irc, args):
    pass

def handle_903(irc, args):
    irc.send("CAP END")

def handle_904(irc, args):
    sys.exit(1)

def handle_905(irc, args):
    sys.exit(1)

