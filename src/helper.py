import json
import os

# Default path in the filesystem where the config.json is located
DEFAULT_CONFIG_FILEPATH = "config/config.json"

# Singleton variable holding the JSON file (config.json)
config = None


def open_json_file(filepath):
    """Open a JSON file from a path and return its content"""
    try:
        with open(filepath) as json_file:
            return json.load(json_file)

    except FileNotFoundError:
        print("File " + filepath + " doesn't exist or can't be opened!",
              "\nCreate a config.json file and put your Bot Token in it!")


def getMessage(update):
    """
    Get the last message from 'update' or 'update.callback_query' Useful when a
    callback is called from both CommandHandler and CallbackQueryHandler
    """
    if(update.message):
        return update.message
    else:
        return update.callback_query.message


def create_folders_and_files(folder, files):
    """
    Check if a folder exists. If not, create it. For each file, if doesn't
    exist, create it inside the folder with a default JSON scheme
    """
    if(not os.path.isdir(folder)):
        os.makedirs(folder)

    for file in files:
        filepath = folder + "/" + file + ".json"
        if(not os.path.exists(filepath)):
            print("-> Created file " + filepath)
            with open(filepath, "w") as outfile:
                json_scheme = {}
                json_scheme['computers'] = []
                json.dump(json_scheme, outfile)
