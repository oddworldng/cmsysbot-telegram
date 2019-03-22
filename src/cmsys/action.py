from wakeonlan import send_magic_packet
import paramiko

from typing import List


def wake_on_lan(target_mac: str):
    send_magic_packet(target_mac)


def shutdown_computer(client: paramiko.SSHClient, target_ip: str, username: str,
                      password: str):

    command = 'init 0'
    send_command_as_root(client, target_ip, username, password, command)


# TODO: Maybe also should return exit code ($?)
def send_command_as_root(client: paramiko.SSHClient, target_ip: str,
                         username: str, password: str, command: str):

    full_command = " sshpass -p %(password)s ssh -o ConnectTimeout=3 %(username)s@%(target_ip)s 'echo %(password)s | sudo -S %(command)s'" % {
        'password': password,
        'username': username,
        'target_ip': target_ip,
        'command': command
    }

    stdin, stdout, stderr = client.exec_command(full_command)

    # Log command on console
    print("User %s executed %s on %s" % (username, command, target_ip))

    # Return output
    return stdout.read().decode('utf-8')
