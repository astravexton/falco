from utils import add_cmd
form ast import literal_eval

@add_cmd
def calc(irc, source, msgtarget, args):
    try:
        irc.msg(msgtarget, eval(args, {}, {}))
    except ValueError:
        irc.msg(msgtarget, "That's not gonna work");
