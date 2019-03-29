import glob
import os.path
import re


def get_local_plugins():
    """Get plugins names from local path."""

    # Set plugins path
    path = "plugins/*"

    # Get plugins file names
    files = glob.glob(path)

    # Filter file names by basename and capitalize
    names = dict(("plugin-%s" % x,
                  os.path.basename(x).capitalize().replace("_", " "))
                 for x in files)

    print("Plugins: %s" % names)

    return names


def get_plugin_arguments(plugin_name: str):

    with open(plugin_name, 'r') as content:
        for line in content:
            match = re.search("^#\s*CMSysBot:\s*(.*)", line)

            if match:
                result = match.group(1).split(',')

                arguments = [
                    command.strip().replace('"', '') for command in result
                ]

                return arguments

