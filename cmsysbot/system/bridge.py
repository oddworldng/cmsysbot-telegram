import logging

from scp import SCPClient

from utils import Session

logger = logging.getLogger("CMSysBot")


def run(session: Session, command: str):
    return _execute_command_bridge(session, command)


def run_as_root(session: Session, command: str):
    root_command = ' echo %s | sudo -kS %s' % (session.password, command)
    return _execute_command_bridge(session, root_command)


def _execute_command_bridge(session: Session, command: str):
    _, stdout, stderr = session.client.exec_command(command)

    logger.warning("User %s executed command %s on bridge (%s)" %
                   (session.username, command, session.bridge_ip))

    return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')


def send_file_to_bridge(session: Session, file: str, bridge_path: str):
    scp = SCPClient(session.client.get_transport())

    scp.put(file, bridge_path)

    scp.close()

    logger.warning("User %s sent file %s to bridge (%s)" %
                   (session.username, file, session.bridge_ip))
