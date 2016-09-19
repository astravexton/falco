from utils import *
from html.parser import HTMLParser
import shlex, tempfile, random, math, requests, json
import os, subprocess, socket, sys, threading, re
import multiprocessing, select, sqlite3, code, time
import wikipedia, fnmatch
from bs4 import BeautifulSoup

@add_cmd
def stalk(irc, source, msgtarget, args):
    if isAdmin(irc, source):
        try:
            irc.msg(msgtarget, "{} is in {}".format(args, ", ".join(irc.nicks[args]["channels"])))
        except:
            irc.msg(msgtarget, "I don't see that person or something has broken")

@add_cmd
def info(irc, source, msgtarget, args):
    """info -- returns "Created by nathan/doge, you can find me in ##doge on irc.freenode.net or #programming on irc.subluminal.net"."""
    irc.msg(msgtarget, "Created by nathan/doge, you can find me in ##doge on irc.freenode.net or #programming on irc.subluminal.net")

@add_cmd
def account2nick(irc, source, msgtarget, args):
    """account2nick <wildcard> -- returns matches against <wildcard>"""
    if isAdmin(irc, source):
        if args:
            matches = []
            for nick in irc.nicks:
                if "account" in irc.nicks[nick]:
                    if fnmatch.fnmatch(irc.nicks[nick]["account"], args) == True:
                        matches.append(nick+" ["+irc.nicks[nick]["account"]+"]")
            if len(matches) > 4:
                key = requests.post("http://bin.zyr.io/documents", data="\n".join(matches).encode(), timeout=5).json()
                irc.msg(msgtarget, "http://bin.zyr.io/"+key["key"]+".txt")
            elif len(matches) < 4:
                for match in matches:
                    irc.msg(msgtarget, match)

@add_cmd
def host2nick(irc, source, msgtarget, args):
    """host2nick <wildcard> -- returns matches against <wildcard>"""
    if isAdmin(irc, source):
        if args:
            matches = []
            for nick in irc.nicks:
                if fnmatch.fnmatch(irc.nicks[nick]["host"], args) == True:
                    matches.append(nick+" ["+irc.nicks[nick]["host"]+"]")
            if len(matches) > 4:
                key = requests.post("http://bin.zyr.io/documents", data="\n".join(matches).encode(), timeout=5).json()
                irc.msg(msgtarget, "http://bin.zyr.io/"+key["key"]+".txt")
            elif len(matches) < 4:
                for match in matches:
                    irc.msg(msgtarget, match)

@add_cmd
def ignore(irc, source, msgtarget, args):
    """ignore <nick/host/#channel/wildcard> -- toggles ignore on either nick, host, channel or wildcard"""
    if isOp(irc, source):
        if args:
            if args.lower() not in irc.ignored:
                irc.ignored.append(args.lower())
                irc.msg(msgtarget, "Ignored "+args)
            else:
                irc.ignored.remove(args.lower())
                irc.msg(msgtarget, "Unignored "+args)
        else:
            irc.msg(msgtarget, "ignore <nick/host/#channel>")

@add_cmd
def remove(irc, source, msgtarget, args):
    """remove <#channel> <nick> [reason] -- removes <nick> from <#channel> with optional [reason]"""
    if isOp(irc, source):
        reason = "Goodbye"
        try:
            chan, user, reason = args.split(" ",2)
        except ValueError:
            try:
                chan, user = args.split(" ",1)
            except ValueError:
                irc.msg(msgtarget, "remove <channel> <nick> [reason]")
                return
        irc.chanmodes[chan].append("REMOVE {} {} :{}".format(chan, user, reason))
        if isSelfOp(irc, msgtarget):
            doOpStuff(irc, msgtarget)
        else:
            irc.send("PRIVMSG ChanServ :OP {} {}".format(chan, irc.nick))

@add_cmd
def kickban(irc, source, msgtarget, args):
    if isOp(irc, source):
        bot_commands["ban"](irc, source, msgtarget, args)
        time.sleep(0.5)
        bot_commands["kick"](irc, source, msgtarget, args)

@add_cmd
def kick(irc, source, msgtarget, args):
    """kick <#channel> <nick> [reason] -- kicks <nick> from <#channel> with optional [reason]"""
    if isOp(irc, source):
        reason = "Goodbye"
        try:
            chan, user, reason = args.split(" ",2)
        except ValueError:
            try:
                chan, user = args.split(" ",1)
            except ValueError:
                irc.msg(msgtarget, "kick <channel> <nick> [reason] -- default reason is \"Goodbye\"")
                return
        irc.chanmodes[chan].append("KICK {} {} :{}".format(chan, user, reason))
        if isSelfOp(irc, msgtarget):
            doOpStuff(irc, msgtarget)
        else:
            irc.send("PRIVMSG ChanServ :OP {} {}".format(chan, irc.nick))

@add_cmd
def ban(irc, source, msgtarget, args):
    if isOp(irc, source):
        reason = None
        try:
            chan, user = args.split(" ",1)
        except ValueError:
            irc.msg(msgtarget, "ban <channel> <nick/host>")
            return
        if len(user.split(" ", 1)) > 1:
            user, reason = user.split(" ", 1)
        try:
            bmask = "*!*@"+irc.nicks[user]["host"]
        except KeyError:
            bmask = user

        irc.chanmodes[chan].append("MODE {} +b {}".format(chan, bmask))
        if "!" not in user or "@" not in user or "*" not in user:
            irc.chanmodes[chan].append("{} {} {} :{}".format(irc.conf["kickmethod"], chan, user, "Goodbye" if not reason else reason))
        if isSelfOp(irc, msgtarget):
            doOpStuff(irc, msgtarget)
        else:
            irc.send("PRIVMSG ChanServ :OP {} {}".format(chan, irc.nick))

@add_cmd
def unban(irc, source, msgtarget, args):
    if isOp(irc, source):
        try:
            chan, user = args.split(" ",1)
        except ValueError:
            irc.msg(msgtarget, "unban <channel> <nick/host>")
        try:
            bmask = "*!*@"+irc.nicks[user]["host"]
        except KeyError:
            bmask = user
        irc.chanmodes[chan].append("MODE {} -b {}".format(chan, bmask))
        if isSelfOp(irc, msgtarget):
            doOpStuff(irc, msgtarget)
        else:
            irc.send("PRIVMSG ChanServ :OP {} {}".format(chan, irc.nick))

@add_cmd
def unquiet(irc, source, msgtarget, args):
    if isOp(irc, source):
        try:
            chan, user = args.split(" ",1)
        except ValueError:
            irc.msg(msgtarget, "unquiet <channel> <nick/host>")
            return
        try:
            bmask = "*!*@"+irc.nicks[user]["host"]
        except KeyError:
            bmask = user

        irc.chanmodes[chan].append("MODE {} -q {}".format(chan, bmask))
        if isSelfOp(irc, msgtarget):
            doOpStuff(irc, msgtarget)
        else:
            irc.send("PRIVMSG ChanServ :OP {} {}".format(chan, irc.nick))

@add_cmd
def quiet(irc, source, msgtarget, args):
    if isOp(irc, source):
        try:
            chan, user = args.split(" ",1)
        except ValueError:
            irc.msg(msgtarget, "quiet <channel> <nick/host>")
            return
        try:
            bmask = "*!*@"+irc.nicks[user]["host"]
        except KeyError:
            bmask = user

        irc.chanmodes[chan].append("MODE {} +q {}".format(chan, bmask))
        if isSelfOp(irc, msgtarget):
            doOpStuff(irc, msgtarget)
        else:
            irc.send("PRIVMSG ChanServ :OP {} {}".format(chan, irc.nick))

@add_cmd
def help(irc, source, msgtarget, args):
    try:
        irc.msg(source.nick, bot_commands[args].__doc__)
    except:
        cmds = ", ".join(bot_commands.keys())
        irc.msg(source.nick, "Commands: {}".format(cmds))

def _exec(irc, source, msgtarget, args):
    if isAdmin(irc, source):
        try:
            s = exec(args)
            if s:
                for line in str(s).split("\n"):
                    irc.msg(msgtarget, line)
        except BaseException as e:
            irc.msg(msgtarget, "{}: {}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))

add_cmd(_exec, ">")

def _shell(irc, source, msgtarget, args):
    if isAdmin(irc, source):
        command = "/bin/bash -c {}".format(shlex.quote(args[1]+" | ircize --remove"))
        start, lines, dump = time.time(), 0, []
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process.stdout.read().decode()
            stderr = process.stderr.read().decode()
            for line in output.split("\n"):
                if line:
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
            irc.msg(msgtarget, "Output too long, see http://bin.zyr.io/"+key)
        elif lines < 10 and not args[0]:
            for line in dump:
                if line:
                    irc.msg(msgtarget, line)

add_regex(_shell, "^\$(\$)? (.*)")

def choose(irc, source, msgtarget, args):
    choices = args[0].split(",")
    if len(choices) > 1 and choices:
        choice = random.choice(choices).strip()
        if choice:
            irc.send("PRIVMSG {} :{}: {}".format(msgtarget, source.nick, choice))
        elif not choice:
            irc.msg(msgtarget, "{}: I can't give you any choice".format(source.nick))
    elif len(choices) == 1:
        irc.send("PRIVMSG {} :{}: {}".format(msgtarget, source.nick, args[0]))

add_regex(choose, "^\.choose (.*)")

def getinfo(irc, source, msgtarget, args):
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
    pipe = os.popen("git log --oneline | head -n1")
    ver = pipe.read().split(" ")[0]
    pipe.close()
    memory = round(int(memory)/1000)
    rx = int(math.log(irc.rx,2)/10.0)
    tx = int(math.log(irc.tx,2)/10.0)
    formats = ["bytes", "KiB", "MiB", "GiB", "TiB"]
    txn = int(irc.tx / (1024 ** tx))
    rxn = int(irc.rx / (1024 ** rx))
    irc.msg(msgtarget, "{}; rx {} {}, tx {} {}; Online for {}; I have seen {} messages and sent {} messages".format(
            ver, rxn, formats[rx], txn, formats[tx],
            timesince(irc.started), irc.rxmsgs, irc.txmsgs))

add_cmd(getinfo, "getinfo")

def _alias(irc, source, msgtarget, args):
    if args.count(" ") == 2:
        args = args.split(" ")
        if args[0] == "add":
            target, alias = args[1:]
            if target in bot_commands:
                bot_commands[alias] = bot_commands[target]
                irc.msg(msgtarget, "Added alias \x02{}\x02 to \x02{}\x02".format(alias, target))
            else:
                irc.msg(msgtarget, "Command \x02{}\x02 does not exist".format(target))
    elif args.count(" ") == 1:
        args = args.split(" ")
        if args[0] == "del":
            target = args[1]
            if target in bot_commands:
                del bot_commands[target]
                irc.msg(msgtarget, "Removed alias \x02{}\x02".format(target))
            else:
                irc.msg(msgtarget, "Alias \x02{}\x02 does not exist".format(target))
    else:
        irc.msg(msgtarget, "Usage: alias <add/del> <target> [alias]")

#add_cmd(_alias, "alias")

@add_cmd
def autokick(irc, source, msgtarget, args):
    """autokick <nick/host>"""
    if isAdmin(irc, source):
        if args:
            if args[0] != "#":
                if args in irc.autokick[msgtarget]:
                    irc.autokick[msgtarget].remove(args)
                    irc.msg(msgtarget, "Removed {} from autokick.".format(args))
                elif args not in irc.autokick[msgtarget]:
                    irc.autokick[msgtarget].append(args)
                    irc.msg(msgtarget, "Added {} to autokick.".format(args))
            else:
                try:
                    kicks = ", ".join(irc.autokick[args]) if irc.autokick[args] else ""
                    irc.msg(msgtarget, "Autokicks on {}: {}".format(args, kicks))
                except KeyError:
                    irc.msg(msgtarget, "I am not on that channel")
        else:
            kicks = ", ".join(irc.autokick[msgtarget]) if irc.autokick[msgtarget] else ""
            irc.msg(msgtarget, "Autokicks on {}: {}".format(msgtarget, kicks))

@add_cmd
def whoami(irc, source, msgtarget, args):
    irc.msg(msgtarget, "{}; admin: {}; op: {}".format(source.hostmask,
        1 if isAdmin(irc, source) else 0,
        1 if isOp(irc, source) else 0))

@add_cmd
def rdns(irc, source, msgtarget, args):
    try:
        irc.msg(msgtarget, socket.gethostbyaddr(args)[0])
    except socket.herror as e:
        irc.msg(msgtarget, e)

@add_cmd
def regex(irc, source, msgtarget, args):
    c = 0
    total = 0
    irc.channels[msgtarget]["buffer"].pop()
    irc.channels[msgtarget]["buffer"].reverse()
    for line in irc.channels[msgtarget]["buffer"]:
        m = re.search(args, line)
        if m:
            if c < 3:
                irc.msg(msgtarget, line)
                c+=1
            else:
                total+=1
    if total > 1:
        irc.msg(msgtarget, "and {} more lines".format(total))
    irc.channels[msgtarget]["buffer"].reverse()

def zeroclick(irc, source, msgtarget, args):
    params = {"q":args[0]}
    url = "http://duckduckgo.com/lite/?"
    #try:
    data = requests.get(url, params=params).content.decode()
    search = re.findall("""\t<td>.\t\s+(.*?).<\/td>""",data,re.M|re.DOTALL)
    if search:
        answer = HTMLParser().unescape(search[-1].replace("<br>"," ").replace("<code>"," ").replace("</code>"," "))
        answer = re.sub("<[^<]+?>"," ",answer)
        out = re.sub("\s+"," ",answer.strip())
        if out:
            #if len(out.split(" More at")[0].split("}")[-1].strip()) < 400:
            irc.msg(msgtarget, out.split(" More at")[0].split("}")[-1].strip())
            #else:
            #    irc.msg(source.split("!")[0], out.split(" More at")[0].split("}")[-1].strip())
        else: 
            irc.msg(msgtarget, "No results")
    else:
        irc.msg(msgtarget, "No results found.")

add_regex(zeroclick, "^>\?(.*)")

def metrictime(irc, source, msgtarget, args):
    "metrictime <current/<hours(0-23)>:<minutes(0-59)>:<seconds(0-59)>> -- convert 24-hour time into metric time"
    args = args[0] if args[0] != "now" else time.strftime("%H:%M:%S")
    if args.count(":") == 2:
        hours,minutes,seconds = args.split(":")
        try:
            hours = int(hours)
            minutes = int(minutes)
            seconds = int(seconds)
        except:
            irc.msg(msgtarget, "That's not a time")
        if hours < 0 or hours >= 24: irc.msg(msgtarget, "Hours must be between 0 and 23")
        elif minutes < 0 or minutes >= 60: irc.msg(msgtarget, "Minutes must be between 0 and 59")
        elif seconds < 0 or seconds >= 60: irc.msg(msgtarget, "Seconds must be between 0 and 59")
        else:
            daysecs = 3600*hours + 60*minutes + seconds
            metricsecs = daysecs * 100000 / 86400
            metrichours = math.floor(metricsecs / 10000)
            metricsecs = metricsecs - 10000 * metrichours
            metricminutes = math.floor(metricsecs / 100)
            metricsecs = math.floor(metricsecs - 100 * metricminutes)
            if metrichours <= 9: metrichours = "0"+str(metrichours)
            if metricminutes <= 9: metricminutes = "0"+str(metricminutes)
            if metricsecs <= 9: metricsecs = "0"+str(metricsecs)
            metrichours = str(metrichours).split(".")[0]
            metricminutes = str(metricminutes).split(".")[0]
            metricsecs = str(metricsecs).split(".")[0]
            metric = metrichours+":"+metricminutes+":"+metricsecs
            irc.msg(msgtarget,  "%s in metric: %s"%(args,metric))
    else:
        irc.msg(msgtarget,  metrictime.__doc__)

add_regex(metrictime, "^\.metric (.*)")

def diplomaticshark(irc, source, msgtarget, args):
    r = requests.get("http://diplomaticshark.com/").content.decode()
    m = re.search("<center><font face=\"Fixedsys, System, Charcoal CY, Chicago\" size=\"7\">(.*?)<\/font>", r)
    if m:
        irc.hasink = False
        irc.msg(msgtarget, m.group(1), reply="PRIVMSG")
        irc.hasink = True

add_cmd(diplomaticshark, "SHARK")

@add_cmd
def ddg(irc, source, msgtarget, args):
    try:
        irc.msg(msgtarget, search(args.replace(" "+args.split(" ")[-1], ""), int(args.split(" ")[-1])))
    except:
        irc.msg(msgtarget, search(args))

@add_cmd
def randwiki(irc, source, msgtarget, args):
    rand = wikipedia.random(pages=1)
    url = wikipedia.page(rand).url
    irc.msg(msgtarget, "Random Article: {} - \x1d{}\x1d".format(rand, url))
    irc.msg(msgtarget, wikipedia.summary(rand, sentences=2, chars=250, auto_suggest=True))

@add_cmd
def wiki(irc, source, msgtarget, args):
    try:
        url = wikipedia.page(args).url
        page = wikipedia.summary(wikipedia.search(args)[0], sentences=2, auto_suggest=True)
        irc.msg(msgtarget, page)
        irc.msg(msgtarget, "More at \x1d"+url)
    except wikipedia.exceptions.DisambiguationError as e:
        bot_commands["wiki"](irc, source, msgtarget, e.options[0])
    except wikipedia.exceptions.PageError:
        irc.msg(msgtarget, "No page could be found")

def search(q, n=0):
    r = requests.get("http://duckduckgo.com/lite",
        params={"q":q.encode('utf8', 'ignore')},
        headers={"User-Agent": "falco IRC bot nathan@irc.subluminal.net/#programming"}
    )
    if r.ok:
        page = BeautifulSoup(r.content.decode())
        results = page.find_all("a")[1:]
        for result in results:
            if "nofollow" in result.decode():
                res = result.decode()
                break
        if res:
            m = re.search("""href="(.*)" rel="nofollow">(.*)<\/a>""", res)
            if m:
                return "{} - \x1d{}\x1d".format(HTMLParser().unescape(re.sub("<[^<]+?>", "", m.group(2))), shorten(m.group(1)))
        else:
            return "No results found"
    else:
        return r.statuc_code

def filter(irc, source, msgtarget, args):
    if isAdmin(irc, source):
        if args.lower().strip() not in irc.filter:
            irc.msg(msgtarget, "{} added to filter".format(args))
            irc.filter.append(args.lower().strip())
        else:
            irc.filter.remove(args.lower().strip())
            irc.msg(msgtarget, "{} removed from filter".format(args))

add_cmd(filter, "filter")

@add_cmd
def mode(irc, source, msgtarget, args):
    if isOp(irc, source):
        try:
            chan, cmd = args.split(" ",1)
            irc.chanmodes[chan].append("MODE {} {}".format(chan, cmd))
            if isSelfOp(irc, msgtarget):
                doOpStuff(irc, msgtarget)
            else:
                irc.send("PRIVMSG ChanServ :OP {} {}".format(chan, irc.nick))
        except ValueError:
            irc.msg(msgtarget, "mode <channel> <modes>")

@add_cmd
def history(irc, source, msgtarget, args):
    c = 0
    word = None
    if args.count(" ") == 1:
        try:
            word, count = args.split(" ",1)
        except ValueError:
            try:
                count = int(args)
            except ValueError:
                count = 10
    else:
        try:
            count = int(args)
        except ValueError:
            word = args
            count = 10
    count = int(count)
    data = []
    if count > 20:
        if word:
            for line in irc.channels[msgtarget]["buffer"][-count:]:
                if re.search(word, line):
                    data.append(line)
            data = "\n".join(data)
        else:
            data = "\n".join(irc.channels[msgtarget]["buffer"][-count:])
        key = requests.post("http://bin.zyr.io/documents", data=data.encode(), timeout=5).json()
        irc.msg(msgtarget, source.nick+": http://bin.zyr.io/"+key["key"])
    else:
        for line in irc.channels[msgtarget]["buffer"][-count:]:
            if c < int(count):
                if word and word in line:
                    irc.msg(source.nick, line)
                elif not word:
                    irc.msg(source.nick, line)
                c +=1
