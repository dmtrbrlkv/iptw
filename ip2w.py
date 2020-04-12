import json
import os
import requests
import logging
from http import HTTPStatus

from wsgiref.simple_server import make_server


def application(environ, start_response):
    ip = environ["PATH_INFO"].split("/")[-1]
    logging.debug(f"IP = {ip}, environ = {environ}")
    try:
        data = get_weather(ip, ipinfo_url, ipinfo_token, owm_url, owm_appid)
        logging.debug(data)
        start_response("200 OK", [("Content-Type", "application/json; charset=utf-8")])
        data = json.dumps(data, ensure_ascii=False)
        data = data.encode("utf-8")
        return [data]

    except Exception as e:
        logging.exception(f"IP = {ip}, error: ")
        start_response(f"500 Internal Server Error", [("Content-Type", "text/html; charset=utf-8")])
        data = f"<h1 style='color:blue'>Can't get weather for {ip}</h1>"
        data = data.encode("utf-8")
        return [data]


def load_config(cfg_path="ip2w.json"):
    default_config = {
        "ipinfo_url": "http://ipinfo.io/{ip}?token={token}",
        "owm_url": "http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={appid}&lang=ru&units=metric",
        "log": None,
        "log_format": "[%(asctime)s] %(levelname).1s %(message)s",
        "log_datefmt":"%Y.%m.%d %H:%M:%S"
    }

    if not os.path.exists(cfg_path):
        raise FileExistsError(f"Config {cfg_path} not found")

    with open(cfg_path) as f:
        config = json.load(f)
    for key, value in default_config.items():
        if key not in config:
            config[key] = value

    return config


def get_weather_by_geo(lat, lon, owm_url, owm_appid):
    url = owm_url.format(lat=lat, lon=lon, appid=owm_appid)
    response = requests.get(url)
    if response.status_code != HTTPStatus.OK:
        raise requests.HTTPError(f"Response status = {response.status_code}")
    if "application/json" not in response.headers["content-type"]:
        raise requests.HTTPError(f"content-type = {response.headers['content-type']}")

    res_json = response.json()
    if "main" not in res_json:
        raise KeyError(f"main not in response - {res_json}")

    if "weather" not in res_json:
        raise KeyError(f"weather not in response - {res_json}")

    temp = res_json["main"]["temp"] if "temp" in res_json["main"] else "-"
    conditions = res_json["weather"][0]["description"] if "description" in res_json["weather"] [0]else "-"

    return temp, conditions


def get_geo(ip, ipinfo_url, ipinfo_token):
    if ip == "":
        raise ValueError("Empty ip")
    url = ipinfo_url.format(ip=ip, token=ipinfo_token)
    response = requests.get(url)
    if response.status_code != HTTPStatus.OK:
        raise requests.HTTPError(f"IP = {ip}, response status = {response.status_code}")
    if "application/json" not in response.headers["content-type"]:
        raise requests.HTTPError(f"content-type = {response.headers['content-type']}")

    res_json = response.json()

    if "loc" not in res_json:
        raise KeyError(f"loc not in response - {res_json}")

    lat, lon = res_json["loc"].split(",")
    city = res_json["city"]

    return lat, lon, city


def get_weather(ip, ipinfo_url, ipinfo_token, owm_url, owm_appid):
    lat, lon, city = get_geo(ip, ipinfo_url, ipinfo_token)
    temp, conditions = get_weather_by_geo(lat, lon, owm_url, owm_appid)
    return {
        "city": city,
        "temp": str(int(temp)) if temp <= 0 else "+" + str(int(temp)),
        "conditions": conditions
    }


cfg_path = os.environ.get('IP2W_CONFIG')
if not cfg_path:
    config = load_config()
else:
    config = load_config(cfg_path)


ipinfo_token = config["ipinfo_token"]
ipinfo_url = config["ipinfo_url"]
owm_url = config["owm_url"]
owm_appid = config["owm_appid"]

logging.basicConfig(filename=config["log"],
                    level=logging.INFO if "debug" not in config or not config["debug"] else logging.DEBUG,
                    format=config["log_format"],
                    datefmt=config["log_datefmt"]
)

logging.info("IP2W started")
logging.debug(f"config from {cfg_path}")
logging.debug(f"congig={config}")


if __name__ == "__main__":
    httpd = make_server('localhost', 80, application)
    httpd.serve_forever()
