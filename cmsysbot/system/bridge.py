import os
import re
from typing import List

from paramiko import SSHClient
from scp import SCPClient

from utils import Session, states


def run(session: Session, command: str):

    return _execute_command_bridge(session, command)


def run_as_root(session: Session, command: str):

    print("Running as root!!!")
    root_command = ' echo %s | sudo -S %s' % (session.password, command)
    return _execute_command_bridge(session, root_command)


def send_file_to_bridge(session: Session, file: str, bridge_path: str):

    scp = SCPClient(session.client.get_transport())

    scp.put(file, bridge_path)

    scp.close()


def _execute_command_bridge(session: Session, command: str):

    _, stdout, stderr = session.client.exec_command(command)
    return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')


# TODO: Maybe also should return exit code ($?)
def run_in_remote_as_root(session: Session, target_ip: str, command: str):

    full_command = (
        " sshpass -p %(password)s ssh -o ConnectTimeout=3 %(username)s@%(target_ip)s 'echo %(password)s | sudo -S %(command)s'"
        % {
            'password': session.password,
            'username': session.username,
            'target_ip': target_ip,
            'command': command
        })

    _, stdout, _ = session.client.exec_command(full_command)

    # Log command on console
    print("User %s executed %s on %s" % (session.username, command, target_ip))

    # Return output
    return stdout.read().decode('utf-8')


def run_plugin_in_remote_as_root(session: Session, target_ip: str,
                                 plugin: List[str]):

    plugin_path_bridge = plugin[0]

    plugin_name = os.path.basename(plugin_path_bridge)

    plugin_path_remote = "%s/%s" % (states.config_file.remote_tmp_dir,
                                    plugin_name)

    print("Plugin name: " + plugin_name)
    print("Route in bridge: " + plugin_path_remote)
    print("Route in remote: " + plugin_path_remote)

    send_file_to_remote(session, target_ip, plugin_path_bridge,
                        plugin_path_remote)

    plugin[0] = plugin_path_remote
    plugin_command = " ".join(plugin)

    output = run_in_remote_as_root(session, target_ip, plugin_command)

    return output


def send_file_to_remote(session: Session, target_ip: str, file: str,
                        remote_path: str):

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
