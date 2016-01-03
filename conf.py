import json

with open("config.json", 'r') as f:
    global conf
    conf = json.load(f)
