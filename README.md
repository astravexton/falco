# falco

IRC bot that does stuff, now supports multiple connections!

# config file

```json
{
    "api_keys": {
        "youtube": "jisghruohruivyty347t4cy734"
    },
    "servers": {
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
            "admins": {"hosts": ["*!*@*"], "accounts": ["falco"]},
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
}

```

To run the bot, first do `sudo pip3 install -r requirements.txt`, then `python3 falco.py config.json`

------------------------------------

Does not run on Windows and I don't plan on fixing it so it does, if you manage to get it running on
Windows, send a pull request.
