from utils import add_cmd, api_keys
import requests, json

def main(irc):
    try:
        os.mkdir("data")
    except:
        pass
    try:
        irc.weather = json.load(open("data/"+irc.server+"-weather.json"))
    except:
        irc.weather = {}
        f = open("data/"+irc.server+"-weather.json", "w")
        f.write("{}")
        f.close()

@add_cmd
def weather(irc, target, args, cmdargs):
    try:
        loc = cmdargs or irc.weather[args.sender.nick]
    except KeyError:
        irc.msg(target, "Enter a location")
        return
    try:
        if ", " in loc:
            lat, lon = loc.split(", ")
            data = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"lat": lat, "lon": lon, "appid": api_keys["weather"], "units": "metric"}, headers={"user-agent":"Mozilla/5.0 (X11; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0"}).json()
        else:
            data = requests.get('http://api.openweathermap.org/data/2.5/weather', params={"q":loc,"units":"metric","appid":api_keys["weather"]},headers={"user-agent":"Mozilla/5.0 (X11; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0"}).json()
        city = u"{}, {}".format(data["name"],data["sys"]["country"])
        temp_C = round(float(data["main"]["temp"]), 1)
        temp_F = CtoF(temp_C)
        humidity = data["main"]["humidity"]
        wind_speed_mph = round(data["wind"]["speed"], 1)
        wind_speed_kmh = MPHtoKMH(wind_speed_mph)
        wind_direction = DEGtoDIR(int(data["wind"]["deg"]))
        clouds_description = data["weather"][0]["main"]
        irc.weather[args.sender.nick] = loc
        f = open("data/"+irc.server+"-weather.json", "w")
        f.write(json.dumps(irc.weather))
        f.close()
        irc.msg(target, u"{}: Currently {}C ({}F), humidity: {}%, wind: {} at {}mph ({}km/h), conditions: {}.".format(
           city,temp_C,temp_F,humidity,wind_direction,wind_speed_mph,wind_speed_kmh,clouds_description))
    except BaseException as e:
        irc.msg(target, "Location not found")

@add_cmd
def forecast(irc, target, args, cmdargs):
    loc = cmdargs or irc.weather[args.sender.nick]
    try:
        if ", " in loc:
            lat, lon = loc.split(", ")
            data = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"lat": lat, "lon": lon, "appid": api_keys["weather"], "units": "metric"}, headers={"user-agent":"Mozilla/5.0 (X11; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0"}).json()
        else:
            data = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={"q": loc, "type": "like", "units": "metric", "appid":api_keys["weather"]}, headers={"user-agent":"Mozilla/5.0 (X11; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0"}).json()
        city = "{}, {}".format(data["city"]["name"],data["city"]["country"])
        data = data["list"][0]
        temp_C = int(data["main"]["temp"])
        temp_F = CtoF(temp_C)
        temp_C_min = round(data["main"]["temp_min"], 1)
        temp_C_max = round(data["main"]["temp_max"], 1)
        temp_F_min = CtoF(temp_C_min)
        temp_F_max = CtoF(temp_C_max)
        humidity = data["main"]["humidity"]
        wind_speed_mph = round(data["wind"]["speed"], 1)
        wind_speed_kmh = MPHtoKMH(wind_speed_mph)
        wind_direction = DEGtoDIR(int(data["wind"]["deg"]))
        clouds_description = data["weather"][0]["main"]
        irc.weather[args.sender.nick] = loc
        f = open("data/"+irc.server+"-weather.json", "w")
        f.write(json.dumps(irc.weather))
        f.close()
        irc.msg(target, "Tomorrows forecast for {}: temperature: min: {}C / {}F, max: {}C / {}F, humidity: {}%, wind: {} at {}mph / {}km/h, conditions: {}.".format(
            city,temp_C_min,temp_F_min,temp_C_max,temp_F_max,humidity,wind_direction,wind_speed_mph,wind_speed_kmh,clouds_description))
    except:
        irc.msg(target, "Location not found")

def CtoF(c):
    return round(c * 1.8000 + 32 ,1)

def MPHtoKMH(m):
    return round(m * 1.60934, 1)

def DEGtoDIR(d):
    return ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW","N"][int((d + 11.25) / 22.5)]

