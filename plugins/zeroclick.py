from utils import add_cmd, time_expression, seconds_map, parse_time
import time, re, requests, urllib

@add_cmd
def sleep(irc, target, args, cmdargs):
    after = re.match(time_expression, args)
    if after:
        after = parse_time(after.group(1))
        time.sleep(after)
        irc.msg(target, "{} seconds passed".format(after))

@add_cmd
def zeroclick(irc, target, args, cmdargs):
    json = requests.get("http://api.duckduckgo.com/",
        params={"q":args, "format":"json", "no_redirect":"1"},
        headers={"User-Agent": "falco IRC bot nathan@irc.subluminal.net/#programming"}
    ).json()
    abstract = json["AbstractText"]
    abstract_url = json["AbstractURL"]
    stripped_answer = re.sub("\s+", " ", re.sub("<[^<]+?>", " ", json["Answer"])).strip()
    if stripped_answer:
        irc.msg(target, stripped_answer[0:300])
    if abstract:
        irc.msg(target, abstract[0:300])
    if abstract_url:
        irc.msg(target, "More at "+abstract_url)
    if not stripped_answer and not abstract and not abstract_url:
        irc.msg(target, "Nothing found, you can try https://duckduckgo.com/?q={}".format(urllib.request.quote(args)))
