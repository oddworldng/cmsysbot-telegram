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


def get_department_names():
    department_names = []
    department_names.extend(get_multiple_department_names())
    department_names.extend(get_single_department_names())

    return department_names


def get_multiple_department_names():
    return [o['name'] for o in config['structure']['multiple']]


def get_single_department_names():
    return config['structure']['single']


def get_section_names_for_department(department):
    index = get_multiple_department_names().index(department)
    section_names = config['structure']['multiple'][index]['sections']

    return section_names


def create_folder_structure_from_config(root, singles, multiples):
    """
    Check if a folder exists. If not, create it. For each file, if doesn't
    exist, create it inside the folder with a default JSON scheme
    """
    for single in singles:
        create_json_if_not_exists(root + single + '.json')

    for multiple in multiples:
        folder = root + multiple['name'] + '/'
        create_folder_if_not_exists(folder)

        for section in multiple['sections']:
            filepath = folder + section + '.json'
            create_json_if_not_exists(filepath)


def create_folder_if_not_exists(folder):
    if(not os.path.isdir(folder)):
        os.makedirs(folder)


def create_json_if_not_exists(filepath):
    if(not os.path.exists(filepath)):
        print("-> Created file " + filepath)
        with open(filepath, "w") as outfile:
            json_scheme = {}
            json_scheme['computers'] = []
            json.dump(json_scheme, outfile)
