import json

DEFAULT_FILEPATH = "config/config.json"


def open_json_file(filepath=DEFAULT_FILEPATH):
    if not filepath:
        filepath = DEFAULT_FILEPATH

    try:
        with open(filepath) as json_file:
            return json.load(json_file)

    except FileNotFoundError:
        print("File " + filepath + " doesn't exist or can't be opened!",
              "\nCreate a config.json file and put your Bot Token in it!")
