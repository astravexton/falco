# falco

IRC bot that does stuff, now supports multiple connections!

# config file

```json
{
    "server1": {
        "netname": "server1",
        "active": true,
        "server": "irc.moo.net",
        "port": 6697,
        "ssl": true,
        "nick": "falco",
        "ident": "falco",
        "gecos": "falco",
        "prefix": "[.>]",
        "reply": "PRIVMSG",
        "modes": "+B",
        "nickserv_password": "",
        "sasl": false,
        "sasl_username": "",
        "sasl_password": "",
        "admins": ["*!*@some.host", "moo!hue@*"],
        "autojoin": ["##test"],
        "kickmethod": "KICK",
        "ignored": [],
        "filter": {},
        "autokick": {},
        "blacklisted_commands": {"#test": ["yt"]},
        "donotlog": []
    },
    "server2": {
        ...
    }
}

```

To run the bot, first do `sudo pip3 install -r requirements.txt`, then `python3 falco.py <config.json>`

------------------------------------

I have no idea if this runs on Windows and don't plan on adding support for it if it doesn't.
Please do not bug me about this as I won't help.
