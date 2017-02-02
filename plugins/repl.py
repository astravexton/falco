import code, sys, utils

def main(irc):
    irc.repl = ""
    irc.repls = Repl(irc)
    irc.multirepl = False

class Repl(code.InteractiveConsole):
    def __init__(self, irc):
        code.InteractiveConsole.__init__(self, {
                "falco": irc,
                "utils": utils})
        self.irc = irc
        self.channel = None
        self.buf = ""

    def write(self, data):
        self.buf += data

    def flush(self):
        msg = self.buf.rstrip("\n")
        if len(msg) > 0:
            self.irc.msg(self.channel, msg)
        self.buf = ""

    def run(self, channel, code):
        self.channel = channel
        sys.stdout = self
        self.push(code)
        sys.stdout = sys.__stdout__
        self.flush()

    def showtraceback(self):
        type, value, lasttb = sys.exc_info()
        self.irc.msg(self.channel, "{0}: {1}".format(type.__name__, value))

    def showsyntaxerror(self, filename):
        self.showtraceback()

def repl(irc, target, args, cmdargs):
    if utils.isAdmin(irc, args.sender):
        irc.repls.run(target, cmdargs)

utils.add_cmd(repl, ">>")

def multirepl(irc, target, args, cmdargs):
    if utils.isAdmin(irc, args.sender) and irc.multirepl == True and cmdargs != '"""':
        irc.repl+=cmdargs+"\n"

utils.add_regex(multirepl, "(.*)")

def multireplprefix(irc, target, args, cmdargs):
    if not utils.isAdmin(irc, args.sender):
        return

    if irc.multirepl == True:
        irc.multirepl = False
        irc.repls.run(target, irc.repl)
        irc.repl = ""
    else:
        irc.multirepl = True

utils.add_regex(multireplprefix, '"""')
