import os

import yaml
from dotenv import load_dotenv


def init():
    with open("config/config.yml") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)
            exit()

    if not config.get("elasticsearch"):
        print("Missing 'elasticsearch (host, port)' values in config")
        exit()

    if not config["elasticsearch"].get("api"):
        print("Missing 'elasticsearch.api (id, key)' values in config")
        exit()

    load_dotenv()  # load environment variables from .env

    if api_id := os.getenv("PRT_API_ID"):
        config["api"]["id"] = api_id
    if api_key := os.getenv("PRT_API_KEY"):
        config["api"]["key"] = api_key

    if es_host := os.getenv("PRT_ES_HOST"):
        config["elasticsearch"]["host"] = es_host
    if es_port := os.getenv("PRT_ES_PORT"):
        config["elasticsearch"]["port"] = es_port

    if interval := os.getenv("PRT_TIMERANGE"):
        config["elasticsearch"]["interval"] = interval

    return config


Config = init()
