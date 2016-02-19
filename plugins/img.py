from utils import add_cmd
import requests

@add_cmd
def img(irc, source, msgtarget, args):
    r = requests.get("https://duckduckgo.com/i.js", params={"l":"wt", "o": "json", "q": args, "f": ""})
    if r.ok:
        imglist = r.json()["results"]
        if len(imglist) > 0:
            irc.msg(msgtarget, "{} - {}".format(imglist[0]["title"],imglist[0]["image"]))
        else:
            irc.msg(msgtarget, "No images for {}".format(args))
