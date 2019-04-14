import json
import glob
import os.path
import re
import time
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
    BODY_REGEX = re.compile(r"CMSysBot:\s*({.*})",
                            re.IGNORECASE | re.MULTILINE | re.DOTALL)
    COMMENTS_REGEX = re.compile(r"\n\s*#")

    def __init__(self, path: str):
        self.path = path
        self.data = self.parse_cmsysbot_body()
        print(self.data)

    @property
    def root(self):
        return self.data.root

    @property
    def source(self):
        return self.data.source

    @property
    def arguments(self):
        return self.data.arguments

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def dirname(self):
        return os.path.dirname(self.path)

    @property
    def bridge_path(self):
        return f"{states.config_file.bridge_tmp_dir}/{self.name}"

    @property
    def remote_path(self):
        return f"{states.config_file.remote_tmp_dir}/{self.name}"

    def parse_cmsysbot_body(self):
        with open(self.path, 'r') as textfile:
            content = textfile.read()
            body_match = re.search(self.BODY_REGEX, content)

            if body_match:
                body = body_match.group(1)
                # Remove start line comments
                body = re.sub(self.COMMENTS_REGEX, "\n", body)
                return json.loads(body)

        return None

    def run(self, session: Session):
        print(self.bridge_path)
        print(self.remote_path)

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
