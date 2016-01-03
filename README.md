# falco

IRC bot that does stuff

# config file

```json
{
    "netname": "moo",
    "active": true,
    "server": "irc.some.net",
    "port": 6697,
    "ssl": true,
    "nick": "falco",
    "ident": "falco",
    "gecos": "falco",
    "prefix": "!",
    "reply": "PRIVMSG",
    "modes": "",
    "nickserv_password": "",
    "admins": ["*!falco@*"],
    "ops": [],
    "autojoin": ["#chat"],
    "pushbullet": "",
    "pushbullet_chan": "",
    "ignored": [],
    "filter": {},
    "autokick": {}
}
```


Most of these options you won't need.

To run the bot, type
```
python3 falco.py <config.json>
```
