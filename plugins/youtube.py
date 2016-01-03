import re, requests
from html.parser import HTMLParser
from utils import *

youtube_regex = """<a href="\s\s\/(.*?)&amp(.*?)\n">\n(.*?)\n<\/a>\n<\/div>\n<div(.*?)>\n(.*?)\n<\/div>\n<div(.*?)>\n(.*?)\n<\/div>\n<div(.*?)>\n(.*?)\n<\/div>"""

def youtube(irc, source, msgtarget, args):
    """youtube/yt <query> -- returns the first result for <query>"""
    r = requests.get("https://m.youtube.co.uk/results", params={"search_query":args,"app":"m"}).content.decode()
    videos = re.findall(youtube_regex, r)
    irc.msg(msgtarget, "https://youtu.be/{} \x0304│\x03 {} \x0304│\x03 {} \x0304│\x03 {} \x0304│\x03 {}".format(
            videos[0][0].split("=")[-1],HTMLParser().unescape(videos[0][2]),videos[0][4] or "#Live",HTMLParser().unescape(videos[0][6][3:]),videos[0][8]))

add_cmd(youtube, "yt")
add_cmd(youtube, "youtube")
