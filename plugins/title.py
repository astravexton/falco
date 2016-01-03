from utils import add_regex
from bs4 import BeautifulSoup
from requests import get
import re

def title_snarfer(irc, source, msgtarget, args):
    if msgtarget in irc.title_snarfer_allowed:
        if args[0].split("//")[1].split("/")[0] not in irc.title_snarfer_ignored_urls:
            try:
                title = BeautifulSoup(get(args[0], timeout=3).content.decode()).title.text
                irc.msg(msgtarget, "Title: {}".format(re.sub("\s+", " ", title))[0:250])
            except AttributeError:
                pass

add_regex(title_snarfer, "(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[~!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)")
