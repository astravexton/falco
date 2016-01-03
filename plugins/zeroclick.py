from utils import add_cmd, time_expression, seconds_map, parse_time
import time, re, requests

@add_cmd
def sleep(irc, source, msgtarget, args):
    after = re.match(time_expression, args)
    if after:
        after = parse_time(after.group(1))
        time.sleep(after)
        irc.msg(msgtarget, "{} seconds passed".format(after))

@add_cmd
def zeroclick(irc, source, msgtarget, args):
    json = requests.get("http://api.duckduckgo.com/",
        params={"q":args, "format":"json", "no_redirect":"1"},
        headers={"User-Agent": "falco IRC bot nathan@irc.subluminal.net/#programming"}
    ).json()
    abstract = json["AbstractText"]
    abstract_url = json["AbstractURL"]
    stripped_answer = re.sub("\s+", " ", re.sub("<[^<]+?>", " ", json["Answer"])).strip()
    if stripped_answer:
        irc.msg(msgtarget, stripped_answer[0:300])
    if abstract:
        irc.msg(msgtarget, abstract[0:300])
    if abstract_url:
        irc.msg(msgtarget, "More at "+abstract_url)
