import re, requests
from html.parser import HTMLParser
from utils import *

def youtube(irc, target, args, cmdargs):
    """youtube/yt <query> -- returns the first result for <query>"""
    yt = YTsearch(args)
    s = "http://youtu.be/{url} │ {title} │ {uploader} │ {views} views"
    irc.msg(target, s.format(
        url=yt["items"][0]["id"],
        title=yt["items"][0]["snippet"]["title"],
        uploader=yt["items"][0]["snippet"]["channelTitle"],
        views="{:,}".format(int(yt["items"][0]["statistics"]["viewCount"])))
    )

add_cmd(youtube, "yt")
add_cmd(youtube, "youtube")

