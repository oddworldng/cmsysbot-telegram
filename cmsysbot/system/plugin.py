import glob
import os.path
import re

from utils import states


def get_local_plugins():
    """Get plugins names from local path."""

    # Set plugins path
    path = "%s/*" % states.config_file.plugins_dir

    # Get plugins file names
    files = glob.glob(path)

    # Filter file names by basename and capitalize
    names = dict(("plugin-%s" % x,
                  os.path.basename(x).capitalize().replace("_", " "))
                 for x in files)

    return names


def get_plugin_arguments(plugin_path: str):

    with open(plugin_path, 'r') as content:
        for line in content:
            match = re.search(r"^#\s*CMSysBot:\s*(.*)", line)

            if match:
                result = match.group(1).split(',')

                arguments = [
                    command.strip().replace('"', '') for command in result
                ]

                return arguments

    return None
