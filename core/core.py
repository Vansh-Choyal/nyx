import json
import os

with open('config.json') as config_raw:
    config = json.load(config_raw)

def _resolve_path(file_path):
    if os.path.isabs(file_path):
        return file_path

    return os.path.join(config["current_directory"], file_path)