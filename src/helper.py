import json
import os

DEFAULT_FILEPATH = "config/config.json"

# Variable holding the JSON file
config = None


def open_json_file(filepath=DEFAULT_FILEPATH):
    if not filepath:
        filepath = DEFAULT_FILEPATH

    try:
        with open(filepath) as json_file:
            return json.load(json_file)

    except FileNotFoundError:
        print("File " + filepath + " doesn't exist or can't be opened!",
              "\nCreate a config.json file and put your Bot Token in it!")


def getMessage(update):
    if(update.message):
        return update.message
    else:
        return update.callback_query.message


def create_folders_and_files(folder, files):
    if(not os.path.isdir(folder)):
        os.makedirs(folder)

    for file in files:
        filepath = folder + "/" + file + ".json"
        if(not os.path.exists(filepath)):
            print("Created file " + filepath)
            with open(filepath, "w") as outfile:
                json_scheme = {}
                json_scheme['computers'] = []
                json.dump(json_scheme, outfile)
