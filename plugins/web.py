import requests
import wikipedia
from bs4 import BeautifulSoup
from html.parser import HTMLParser
import re
from utils import add_cmd, add_regex
from urllib import parse

def zeroclick(irc, target, args, cmdargs):
    params = {"q": cmdargs}
    url = "http://duckduckgo.com/lite/?"
    data = requests.get(url, params=params).content.decode()
    search = re.findall("""\t<td>.\t\s+(.*?).<\/td>""",data,re.M|re.DOTALL)
    if search:
        answer = HTMLParser().unescape(search[-1].replace("<br>"," ").replace("<code>"," ").replace("</code>"," "))
        answer = re.sub("<[^<]+?>"," ",answer)
        out = re.sub("\s+"," ",answer.strip())
        if out:
            irc.msg(target, out.split(" More at")[0].split("}")[-1].strip())
        else: 
            irc.msg(target, "No results")
    else:
        irc.msg(target, "No results found.")

add_regex(zeroclick, "^>\?(.*)")

@add_cmd
def ddg(irc, target, args, cmdargs):
    print(search(cmdargs))
    irc.msg(target, search(cmdargs))

@add_cmd
def randwiki(irc, target, args, cmdargs):
    rand = wikipedia.random(pages=1)
    url = wikipedia.page(rand).url
    irc.msg(target, "Random Article: {} - \x1d{}\x1d".format(rand, url))
    irc.msg(target, wikipedia.summary(rand, sentences=2, chars=250, auto_suggest=True))

@add_cmd
def wiki(irc, target, args, cmdargs):
    try:
        url = wikipedia.page(cmdargs).url
        page = wikipedia.summary(wikipedia.search(cmdargs)[0], sentences=2, auto_suggest=True)
        irc.msg(target, page)
        irc.msg(target, "More at \x1d"+url)
    except wikipedia.exceptions.DisambiguationError as e:
        bot_commands["wiki"](irc, target, args, e.options[1])
    except wikipedia.exceptions.PageError:
        irc.msg(target, "No page could be found")

def search(q, n=0):
    r = requests.get("http://duckduckgo.com/lite",
        params={"q": q.encode('utf8', 'ignore')},
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
                return "{} - \x1d{}\x1d".format(HTMLParser().unescape(re.sub("<[^<]+?>", "", m.group(2))), parse.unquote(m.group(1).split("=")[-1]))
        else:
            return "No results found"
    else:
        return r.status_code