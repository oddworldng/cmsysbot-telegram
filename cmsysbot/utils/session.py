import paramiko
from paramiko import ssh_exception


class Session:
    def __init__(self,
                 username: str = "",
                 password: str = "",
                 bridge_ip: str = ""):
        self.username = username
        self.password = password
        self.bridge_ip = bridge_ip

        self.route = []
        self.computers = None

        self.connected = False
        self.client = None

    def start_connection(self):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        # Try to connect to the client
        try:
            self.client.connect(self.bridge_ip, 22, self.username,
                                self.password, allow_agent=False,
                                look_for_keys=False)

            self.connected = True

        except (ssh_exception.NoValidConnectionsError,
                ssh_exception.AuthenticationException):
            # TODO: Rethrow the error?
            self.connected = False

    def end_connetion(self):
        self.username = ""
        self.password = ""
        self.bridge_ip = ""

        self.route = []
        self.computers = None

        self.connected = False
        self.client.close()
