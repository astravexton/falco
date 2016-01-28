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

def repl(irc, source, msgtarget, args):
    if utils.isAdmin(irc, source):
        irc.repls.run(msgtarget, args)

utils.add_cmd(repl, ">>")

def multirepl(irc, source, msgtarget, args):
    args = args[0]
    if utils.isAdmin(irc, source) and irc.multirepl == True and args != '"""':
        irc.repl+=args+"\n"

add_regex(multirepl, "(.*)")

def multireplprefix(irc, source, msgtarget, args):
    if utils.isAdmin(irc, source):
        if irc.multirepl == True:
            irc.multirepl = False
            irc.repls.run(msgtarget, irc.repl)
            irc.repl = ""
        else:
            irc.multirepl = True

utils.add_regex(multireplprefix, '"""')
