import paramiko


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
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy)

        # Try to connect to the client
        self.client.connect(self.bridge_ip, 22, self.username, self.password)

        self.connected = True

    def end_connetion(self):
        self.username = ""
        self.password = ""
        self.bridge_ip = ""

        self.route = []
        self.computers = None

        self.connected = False
        self.client.close()
