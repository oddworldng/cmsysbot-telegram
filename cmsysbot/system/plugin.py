import glob
import os.path
import re

from utils import states


class Plugin:
    BODY_REGEX = re.compile(r"CMSysBot:\s*{(.*)}",
                            re.IGNORECASE | re.MULTILINE | re.DOTALL)
    SOURCE_REGEX = re.compile(r"\"source\"\s*:\s*\"(.*)\"\s*,?", re.IGNORECASE)
    ARGUMENTS_REGEX = re.compile(r"\"arguments\"\s*:\s*\[(.*)\]",
                                 re.MULTILINE | re.DOTALL)
    WORD_REGEX = re.compile(r".*?\"(.*)\"", re.DOTALL)

    def __init__(self, path: str):
        self.path = path

        self.parse_cmsysbot_tag()

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def dirname(self):
        return os.path.dirname(self.path)

    def parse_cmsysbot_tag(self):
        with open(self.path, 'r') as textfile:
            content = textfile.read()

            body_match = re.search(self.BODY_REGEX, content)

            if body_match:
                body = body_match.group(1)

                self.source = self._parse_source(body)
                self.arguments = self._parse_arguments(body)

    def _parse_source(self, body: str):
        source = "remote"  # Default value

        source_match = re.search(self.SOURCE_REGEX, body)

        if source_match:
            source = source_match.group(1)

        return source

    def _parse_arguments(self, body: str):
        arguments = {}

        arguments_match = re.search(self.ARGUMENTS_REGEX, body)

        if arguments_match:
            raw_arguments = arguments_match.group(1).split(',')

            for word in raw_arguments:
                word_match = re.match(self.WORD_REGEX, word)

                if word_match:
                    arguments[word_match.group(1)] = ""

        return arguments

    @staticmethod
    def get_local_plugins():
        """Get plugins names from local path defined in config."""

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
