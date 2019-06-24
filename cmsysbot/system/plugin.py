import glob
import json
import os.path
import re
from concurrent import futures
from typing import Dict

from cmsysbot.utils import Computer, Session, states


class PluginVar:
    USERNAME = "$USERNAME"
    PASSWORD = "$PASSWORD"
    BRIDGE_IP = "$BRIDGE_IP"
    TARGET_IP = "$TARGET_IP"
    TARGET_MAC = "$TARGET_MAC"
    MACS_LIST = "$MACS_LIST"
    IPS_LIST = "$IPS_LIST"
    SOURCE_BRIDGE = "bridge"
    SOURCE_REMOTE = "remote"
    ROOT = False


class Plugin:
    BODY_REGEX = re.compile(
        r"CMSysBot:\s*({.*?})\s*\n", re.IGNORECASE | re.MULTILINE | re.DOTALL
    )
    COMMENTS_REGEX = re.compile(r"\n\s*#")

    COPY_MODE = 0o555

    def __init__(self, server_path: str):
        self.server_path = server_path
        self.data = self.parse_cmsysbot_body()

        self.arguments = {}
        for key in self.data["arguments"]:
            self.arguments[key] = ""

    @property
    def root(self):
        return self.data["root"]

    @property
    def source(self):
        return self.data["source"]

    @property
    def name(self):
        return os.path.basename(self.server_path)

    @property
    def bridge_path(self):
        return f"{states.config_file.bridge_tmp_dir}/{self.name}"

    @property
    def remote_path(self):
        return f"{states.config_file.remote_tmp_dir}/{self.name}"

    def parse_cmsysbot_body(self):
        with open(self.server_path, "r") as textfile:
            content = textfile.read()
            body_match = re.search(self.BODY_REGEX, content)

            if body_match:
                body = body_match.group(1)
                # Remove start line comments
                body = re.sub(self.COMMENTS_REGEX, "\n", body)
                data = json.loads(body)

                if "arguments" not in data:
                    data["arguments"] = []

                return data

        return None

    def run(self, session: Session):
        session.copy_to_bridge(self.server_path, self.bridge_path, Plugin.COPY_MODE)

        # Replace the session $arguments (username, password...)
        self.fill_session_arguments(session)

        # RUN ON BRIDGE
        if self.source == PluginVar.SOURCE_BRIDGE:
            command = f"{self.bridge_path} {' '.join(self.arguments.values())}"

            yield "Bridge", session.bridge_ip, (
                *session.run_on_bridge(command, root=self.root)
            )

        # RUN ON REMOTE
        else:
            with futures.ThreadPoolExecutor() as executor:
                result_futures = [
                    executor.submit(self._run_on_remote, computer, session)
                    for computer in session.computers.get_included_computers()
                ]

                for future in futures.as_completed(result_futures):
                    yield future.result()

    def _run_on_remote(self, computer: Computer, session: Session):

        session.copy_to_remote(computer.ip, self.bridge_path, self.remote_path)

        # Replace the computer arguments (ip, mac...)
        self.fill_computer_arguments(computer)
        command = f"{self.remote_path} {' '.join(self.arguments.values())}"

        return (
            computer.name,
            computer.ip,
            (*session.run_on_remote(computer.ip, command, self.root)),
        )

    def fill_session_arguments(self, session: Session):

        if PluginVar.USERNAME in self.arguments:
            self.arguments[PluginVar.USERNAME] = session.username

        if PluginVar.PASSWORD in self.arguments:
            self.arguments[PluginVar.PASSWORD] = session.password

        if PluginVar.BRIDGE_IP in self.arguments:
            self.arguments[PluginVar.BRIDGE_IP] = session.bridge_ip

        if PluginVar.MACS_LIST in self.arguments:
            self.arguments[PluginVar.MACS_LIST] = " ".join(
                list(map(lambda c: c.mac, session.computers.get_included()))
            )

        if PluginVar.IPS_LIST in self.arguments:
            self.arguments[PluginVar.IPS_LIST] = " ".join(
                list(map(lambda c: c.ip, session.computers.get_included()))
            )

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
        path = f"{states.config_file.plugins_dir}/*"

        # Get plugins file names
        files = glob.glob(path)

        # Filter file names by basename and capitalize
        names = {}

        for file in files:
            if os.path.basename(file)[0] != "_":

                key = f"plugin-{file}"
                names[key] = os.path.basename(file).capitalize().replace("_", " ")

        return names
