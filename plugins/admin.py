from utils import *
import shlex, math, requests
import os, subprocess, socket, sys, re
import time
import fnmatch

@add_cmd
def info(irc, target, args, cmdargs):
    """info -- returns "Created by nathan/doge, you can find me in ##doge on irc.freenode.net or #programming on irc.subluminal.net"."""
    irc.msg(target, "Created by nathan/doge, you can find me in ##doge on irc.freenode.net or #programming on irc.subluminal.net")

@add_cmd
def ignore(irc, target, args, cmdargs):
    """ignore <nick> -- toggles ignore on a nick"""
    if not isOp(irc, args.sender):
        return

    if not cmdargs:
        irc.msg(target, "ignore <nick>")
        return

    userObj = irc.get_user(cmdargs.lower())
    if userObj.ignored == True:
        userObj.ignored = False
        irc.msg(target, "Unignored {}".format(userObj.nickname))
    else:
        userObj.ignored = True
        irc.msg(target, "Ignored {}".format(userObj.nickname))

@add_cmd
def help(irc, target, args, cmdargs):
    try:
        irc.msg(source.nick, bot_commands[args].__doc__)
    except:
        cmds = ", ".join(bot_commands.keys())
        irc.msg(source.nick, "Commands: {}".format(cmds))

def _exec(irc, target, args, cmdargs):
    if not isAdmin(irc, args.sender):
        return

    try:
        s = exec(cmdargs)
        if not s:
            return

        for line in str(s).split("\n"):
            irc.msg(target, line)
    except BaseException as e:
        irc.msg(target, "{}: {}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))

add_cmd(_exec, ">")

def _shell(irc, target, args, cmdargs):
    "[$]$ <command>"
    irc.msg(target, cmdargs)
    return
    if not isAdmin(irc, args.sender):
        return

    command = "/bin/bash -c {}".format(shlex.quote(cmdargs+" | ircize --remove"))
    start, lines, dump = time.time(), 0, []
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.read().decode()
        stderr = process.stderr.read().decode()
        for line in output.split("\n"):
            if not line:
                break

            dump.append(line)
            lines+=1

        if stderr:
            dump.append(stderr.strip())

        if process.poll() == 0:
            break

        if time.time() - start > 5:
            print("Timeout reached")
            break

    rc = process.poll()
    if lines > 10:
        key = requests.post("https://bin.zyr.io/documents", data=output.encode()).json()["key"]
        irc.msg(target, "Output too long, see http://bin.zyr.io/"+key)
    elif lines < 10 and not args[0]:
        for line in dump:
            if line:
                irc.msg(target, line)

add_regex(_shell, "^\$(\$)? (.*)")

def getinfo(irc, target, args, cmdargs):
    "getinfo -- returns PID, Threads and Virtual Memory"
    PID = os.getpid()
    pipe = os.popen("cat /proc/%s/status" % PID)
    out = pipe.read().split("\n")
    for line in out:
        if line.strip().startswith("Threads:"):
            threads = line.strip().split()[1]
        elif line.strip().startswith("VmRSS:"):
            memory = line.strip().split(":")[1].split(" ")[-2]
    pipe.close()
    ver = bot_version()
    memory = round(int(memory)/1000)
    rx = int(math.log(irc.rx,2)/10.0)
    tx = int(math.log(irc.tx,2)/10.0)
    formats = ["bytes", "KiB", "MiB", "GiB", "TiB"]
    txn = int(irc.tx / (1024 ** tx))
    rxn = int(irc.rx / (1024 ** rx))
    irc.msg(target, "{}; rx {} {}, tx {} {}; Online for {}; I have seen {} messages and sent {} messages".format(
            ver, rxn, formats[rx], txn, formats[tx],
            timesince(irc.started), irc.rxmsgs, irc.txmsgs))

add_cmd(getinfo, "getinfo")

@add_cmd
def whoami(irc, target, args, cmdargs):
    irc.msg(target, "{}; admin: {}; op: {}".format(args.sender.hostmask, isAdmin(irc, args.sender), isOp(irc, args.sender)))

@add_cmd
def rdns(irc, target, args, cmdargs):
    try:
        irc.msg(target, socket.gethostbyaddr(cmdargs)[0])
    except socket.herror as e:
        irc.msg(target, e)

@add_cmd
def regex(irc, target, args, cmdargs):
    c = 0
    total = 0
    chanObj = irc.get_channel(target)
    for line in chanObj.buffer[::-1]:
        m = re.search(cmdargs, line[1])
        if not m:
            pass
        if c < 3:
            irc.msg(target, "%s ago %s" % (timesince(line[0]), line[1]))
            c+=1
        else:
            total+=1
    if total > 1:
        irc.msg(target, "and {} more lines".format(total))
