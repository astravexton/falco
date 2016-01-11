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
    "sasl": true,
    "sasl_username": "falco",
    "sasl_password": "moo",
    "admins": ["*!falco@*"],
    "ops": [],
    "autojoin": ["#chat"],
    "ignored": [],
    "filter": {},
    "autokick": {}
}
```

To run the bot, type
```
python3 falco.py <config.json>
```
