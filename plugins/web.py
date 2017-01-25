import requests
import wikipedia
from bs4 import BeautifulSoup
from html.parser import HTMLParser
import re

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
        return r.status_code