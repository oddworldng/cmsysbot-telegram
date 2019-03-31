import glob
import os.path
import re
from typing import Dict

from system import bridge, remote
from utils import Computer, Session, states


class PluginVar:
    USERNAME = "$USERNAME"
    PASSWORD = "$PASSWORD"
    BRIDGE_IP = "$BRIDGE_IP"
    TARGET_IP = "$TARGET_IP"
    TARGET_MAC = "$TARGET_MAC"
    MACS_LIST = "$MACS_LIST"
    SOURCE_BRIDGE = "bridge"
    SOURCE_REMOTE = "remote"
    ROOT = False


class Plugin:
    BODY_REGEX = re.compile(r"CMSysBot:\s*{(.*)}",
                            re.IGNORECASE | re.MULTILINE | re.DOTALL)
    ROOT_REGEX = re.compile(r"\"root\"\s*:\s*\"(.*)\"\s*,?", re.IGNORECASE)
    SOURCE_REGEX = re.compile(r"\"source\"\s*:\s*\"(.*)\"\s*,?", re.IGNORECASE)
    ARGUMENTS_REGEX = re.compile(r"\"arguments\"\s*:\s*\[(.*)\]",
                                 re.MULTILINE | re.DOTALL)
    WORD_REGEX = re.compile(r".*?\"(.*)\"", re.DOTALL)

    def __init__(self, path: str):
        self.path = path
        self.parse_cmsysbot_body()

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def dirname(self):
        return os.path.dirname(self.path)

    def parse_cmsysbot_body(self):
        with open(self.path, 'r') as textfile:
            content = textfile.read()
            body = ""

            body_match = re.search(self.BODY_REGEX, content)
            if body_match:
                body = body_match.group(1)

            self.root = self._parse_root(body)
            self.source = self._parse_source(body)
            self.arguments = self._parse_arguments(body)

    def _parse_root(self, body: str):
        root = PluginVar.ROOT  # Default value

        root_match = re.search(self.ROOT_REGEX, body)

        if root_match:
            root = (root_match.group(1).lower() == 'true')

        return root

    def _parse_source(self, body: str):
        source = PluginVar.SOURCE_BRIDGE  # Default value

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

    def run(self, session: Session):
        # Get route in bridge
        bridge_plugin_path = "%s/%s" % (states.config_file.bridge_tmp_dir,
                                        self.name)
        # Send plugin to bridge
        bridge.send_file_to_bridge(session, self.path, bridge_plugin_path)

        # Substitute the $USERNAME, $PASSWORD... arguments
        self.fill_session_arguments(session)

        # Run the command only once on the bridge and return
        if self.source == PluginVar.SOURCE_BRIDGE:
            command = "%s %s" % (bridge_plugin_path, " ".join(
                self.arguments.values()))

            computer = Computer({
                "name": "Bridge",
                "ip": session.bridge_ip,
                "mac": ""
            })

            if self.root:
                yield (computer, *bridge.run_as_root(session, command))
            else:
                yield (computer, *bridge.run(session, command))

        # Run the command for each included computer
        elif self.source == PluginVar.SOURCE_REMOTE:

            for computer in session.computers.get_included_computers():
                self.fill_computer_arguments(computer)

                remote_plugin_path = "%s/%s" % (
                    states.config_file.remote_tmp_dir, self.name)

                # Send plugin to remote for execution
                remote.send_file_to_remote(session, computer.ip,
                                           bridge_plugin_path,
                                           remote_plugin_path)

                command = "%s %s" % (remote_plugin_path, " ".join(
                    self.arguments.values()))

                if self.root:
                    yield (computer,
                           *remote.run_as_root(session, computer.ip, command))
                else:
                    yield (computer,
                           *remote.run(session, computer.ip, command))

    def fill_session_arguments(self, session: Session):
        if PluginVar.USERNAME in self.arguments:
            self.arguments[PluginVar.USERNAME] = session.username

        if PluginVar.PASSWORD in self.arguments:
            self.arguments[PluginVar.PASSWORD] = session.password

        if PluginVar.BRIDGE_IP in self.arguments:
            self.arguments[PluginVar.BRIDGE_IP] = session.bridge_ip

        if PluginVar.MACS_LIST in self.arguments:
            self.arguments[PluginVar.MACS_LIST] = " ".join(
                list(session.computers.get_macs()))

    def fill_computer_arguments(self, computer: Computer):
        if PluginVar.TARGET_IP in self.arguments:
            self.arguments[PluginVar.TARGET_IP] = computer.ip

        if PluginVar.TARGET_MAC in self.arguments:
            self.arguments[PluginVar.TARGET_MAC] = computer.mac

    def __getitem__(self, key: str) -> str:
        return self.arguments[key]

    def __setitem__(self, key: str, value: str):
        self.arguments[key] = value

    def __str__(self):
        return self.name

    @staticmethod
    def get_local_plugins() -> Dict[str, str]:
        """Get plugins names from local path defined in config."""

        # Set plugins path
        path = "%s/*" % states.config_file.plugins_dir

        # Get plugins file names
        files = glob.glob(path)

        # Filter file names by basename and capitalize
        names = {}

        for file in files:
            if os.path.basename(file)[0] != '_':

                key = "plugin-%s" % file
                names[key] = os.path.basename(file).capitalize().replace(
                    "_", " ")

        return names
