import os
import re
from typing import List

import paramiko
from wakeonlan import send_magic_packet

from utils import Session


def wake_on_lan(target_mac: str):
    send_magic_packet(target_mac)


def shutdown_computer(client: paramiko.SSHClient, target_ip: str,
                      username: str, password: str):

    command = 'init 0'
    send_command_as_root(client, target_ip, username, password, command)


def get_local_ips(client: paramiko.SSHClient, password: str, macs: List[str]):

    submask = get_submask(client)

    arp_scan_output = run_in_bridge_as_root(client, password,
                                            'arp-scan %s' % submask)

    local_ips = {}

    for line in arp_scan_output.splitlines():
        match = re.search('((?:\d{1,3}\.){3}\d{1,3}).*((?:\w\w:){5}\w\w)',
                          line)

        if match:
            ip = match.group(1)
            mac = match.group(2)

            local_ips[mac] = ip

    return local_ips


def get_submask(client: paramiko.SSHClient):

    command = "ip -o -f inet addr show | awk '/scope global/ {print $4}'"

    return run_in_bridge(client, command)


def update_computer(client: paramiko.SSHClient, target_ip: str, username: str,
                    password: str):

    update = 'apt update'
    upgrade = 'screen -d -m apt upgrade -y'
    dist_upgrade = 'screen -d -m apt dist-upgrade -y'

    print(send_command_as_root(client, target_ip, username, password, update))
    print(send_command_as_root(client, target_ip, username, password, upgrade))
    print(
        send_command_as_root(client, target_ip, username, password,
                             dist_upgrade))


def run_in_bridge(client: paramiko.SSHClient, command: str):

    _, stdout, _ = client.exec_command(command)
    return stdout.read().decode('utf-8')


def run_in_bridge_as_root(client: paramiko.SSHClient, password: str,
                          command: str):

    root_command = ' echo %s | sudo -S %s' % (password, command)

    _, stdout, _ = client.exec_command(root_command)
    return stdout.read().decode('utf-8')


# TODO: Maybe also should return exit code ($?)
def send_command_as_root(client: paramiko.SSHClient, target_ip: str,
                         username: str, password: str, command: str):

    full_command = (
        " sshpass -p %(password)s ssh -o ConnectTimeout=3 %(username)s@%(target_ip)s 'echo %(password)s | sudo -S %(command)s'"
        % {
            'password': password,
            'username': username,
            'target_ip': target_ip,
            'command': command
        })

    _, stdout, _ = client.exec_command(full_command)

    # Log command on console
    print("User %s executed %s on %s" % (username, command, target_ip))

    # Return output
    return stdout.read().decode('utf-8')


def execute_script_as_root(session: Session, target_ip: str, script_path: str):

    script_name = os.path.basename(script_path)

    remote_folder = "/tmp/"

    send_file(session, target_ip, script_path, remote_folder)

    output = send_command_as_root(session.client, target_ip, session.username,
                                  session.password,
                                  remote_folder + script_name)

    return output


def send_file(session: Session, target_ip: str, file: str, remote_path: str):

    full_command = " sshpass -p %(password)s scp %(file)s %(target_ip)s:%(remote_path)s" % {
        'password': session.password,
        'target_ip': target_ip,
        'file': file,
        'remote_path': remote_path
    }

    _, stdout, stderr = session.client.exec_command(full_command)

    print("Scp: " + stderr.read().decode('utf-8'))

    print("User %s sent file %s from %s to %s" %
          (session.username, file, session.bridge_ip, target_ip))


def install_software(client: paramiko.SSHClient, target_ip: str, username: str,
                     password: str, software: str):

    # Generating command
    command = 'apt install -y %s' % software

    # Execute command
    send_command_as_root(client, target_ip, username, password, command)
    _, stdout, _ = client.exec_command(full_command)
