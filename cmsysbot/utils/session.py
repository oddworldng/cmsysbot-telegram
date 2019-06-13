import logging

import paramiko
from paramiko import ssh_exception

from . import states


class Session:
    def __init__(self, username: str = "", password: str = "", bridge_ip: str = ""):
        self.username = username
        self.password = password
        self.bridge_ip = bridge_ip

        self.route = []
        self.computers = None

        self.is_allowed = False
        self.connected = False
        self.client: paramiko.SSHClient = None

    def start_connection(self):

        self.is_allowed = self.__user_acl()

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        # Try to connect to the client
        try:
            if not self.is_allowed:
                raise RuntimeError("User has no access to the section")

            self.client.connect(
                self.bridge_ip,
                22,
                self.username,
                self.password,
                allow_agent=False,
                look_for_keys=False,
            )

            self.connected = True

            logging.getLogger().info(
                f"User {self.username} connected to "
                f"{self.bridge_ip} in {'/'.join(self.route)}"
            )

        except (
            ssh_exception.NoValidConnectionsError,
            ssh_exception.AuthenticationException,
            RuntimeError,
        ):
            # TODO: Rethrow the error?
            self.connected = False

            logging.getLogger().warning(
                f"User {self.username} tried to connect to "
                f"{self.bridge_ip} in {'/'.join(self.route)}"
            )

    def end_connetion(self):

        logging.getLogger().info(
            f"User {self.username} disconnected from {self.bridge_ip} "
            f"in {'/'.join(self.route)}"
        )

        self.username = ""
        self.password = ""
        self.bridge_ip = ""

        self.route = []
        self.computers = None
        self.is_allowed = False

        self.connected = False
        self.client.close()

    def __user_acl(self) -> bool:
        """
        Checks if the user has access to the current defined Section (using the
        self.route attribute).

        Note:
            Access permissions propagate to subsections. That means that if you give
            access to one user, you're also giving him access to all the subsections
            below.
        """

        # Check first if the username is an admin
        if self.username in states.config_file.admins:
            return True

        # If no ACL is defined, all users have access to the section
        no_acl_defined = True

        # Iterate through each Section and its parent, and check the ACL for each one
        route = self.route[:]
        while route:
            section = states.config_file.get_section(route)

            if section.allowed_users:
                no_acl_defined = False

                if self.username in section.allowed_users:
                    return True

            route.pop()

        # If any ACL was defined on this Section or its parents, this will be True.
        # Otherwise, the user has no access, so it will return False.
        return no_acl_defined

    def copy_to_bridge(self, source_path: str, bridge_path: str, permissions: int):

        sftp = self.client.open_sftp()
        sftp.put(source_path, bridge_path, confirm=True)
        sftp.chmod(bridge_path, permissions)

        sftp.close()

    def run_on_bridge(self, command: str, root: bool):

        self.__log_command(self.bridge_ip, command, root)

        if root:
            command = f" echo {self.password} | sudo -kS {command}"

        _, stdout, stderr = self.client.exec_command(command)

        return stdout.read().decode("utf-8"), stderr.read().decode("utf-8")

    def copy_to_remote(self, target_host: str, source_path: str, remote_path: str):

        scp_command = (
            f" sshpass -p {self.password} scp {source_path}"
            f" {target_host}:{remote_path}"
        )

        _, stdout, _ = self.client.exec_command(scp_command)

        # Wait for command to finish
        stdout.read()

    def run_on_remote(self, target_host: str, command: str, root: bool):

        self.__log_command(target_host, command, root)

        if root:
            command = f" echo {self.password} | sudo -kS {command}"

        ssh_command = (
            f" sshpass -p {self.password} ssh -o ConnectTimeout=3"
            f" -o StrictHostKeyChecking=no {target_host} '{command}'"
        )

        _, stdout, stderr = self.client.exec_command(ssh_command)

        return stdout.read().decode("utf-8"), stderr.read().decode("utf-8")

    def __log_command(self, target_ip: str, command: str, root: bool):
        msg = (
            f"User {self.username} executed {'AS ROOT' if root else ''} the command "
            f"{command} on {target_ip} in {'/'.join(self.route)}"
        )

        logging.getLogger().info(msg)
