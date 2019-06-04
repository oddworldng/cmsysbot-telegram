from paramiko import ssh_exception
from utils import states
import logging
import paramiko


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

    def __user_acl(self):
        # Access to user actual section
        section = states.config_file.get_sections(self.route)
        print(section.allowed_users)
        if self.username in section.allowed_users or not section.allowed_users:
            return True
        else:
            return False

    def start_connection(self):

        self.is_allowed = self.__user_acl()
        # Security: check user acl
        if self.is_allowed:

            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

            # Try to connect to the client
            try:
                self.client.connect(
                    self.bridge_ip,
                    22,
                    self.username,
                    self.password,
                    allow_agent=False,
                    look_for_keys=False,
                )
                self.connected = True

                # TODO: Check if sshpass is installed
                # .........

                logging.getLogger().info(
                    f"User {self.username} connected to "
                    f"{self.bridge_ip} in {'/'.join(self.route)}"
                )

            except (
                ssh_exception.NoValidConnectionsError,
                ssh_exception.AuthenticationException,
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

        self.connected = False
        self.client.close()

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
