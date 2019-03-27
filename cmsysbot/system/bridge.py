from paramiko import SSHClient
from scp import SCPClient


def send_file(client: SSHClient, local_path: str, bridge_path: str):

    scp = SCPClient(client.get_transport())

    scp.put(local_path, bridge_path)

    scp.close()

