import os
import json


def load_config():
    config_path = os.environ.get("CONFIG_PATH", "config.json")
    with open(config_path) as f:
        return json.load(f)
