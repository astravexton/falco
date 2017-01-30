from utils import add_cmd, timesince
import subprocess, math, os

@add_cmd
def status(irc, target, args, cmdargs):
    PID = os.getpid()
    size = subprocess.getoutput("pmap -X {PID} | tail -n1".format(PID=PID)).strip().split()
    size = int(size[1]) + int(size[6])
    time = subprocess.getoutput("ps -p {PID} h -o time".format(PID=PID)).strip()
    up = irc.started
    rx = int(math.log(irc.rx,2)/10.0)
    tx = int(math.log(irc.tx,2)/10.0)
    formats = ["bytes", "KiB", "MiB", "GiB", "TiB"]
    txn = int(irc.tx / (1024 ** tx))
    rxn = int(irc.rx / (1024 ** rx))
    irc.msg(target, "This bot has been running for {}, is using {}KB of RAM, has used {} of CPU time, has sent {}{} of data, and received {}{} of data.".format(
        timesince(up), size, time, txn, formats[tx], rxn, formats[rx]))
