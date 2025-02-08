import json


def save_settings(settings, filename="settings.json"):
    with open(filename, "w") as f:
        json.dump(settings, f)

def load_settings(filename="settings.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}