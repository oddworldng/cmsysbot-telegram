from scp import SCPClient
import logging

from utils import Session

logger = logging.getLogger(__main__)


def run(session: Session, command: str):
    return _execute_command_bridge(session, command)


def run_as_root(session: Session, command: str):
    root_command = ' echo %s | sudo -kS %s' % (session.password, command)
    return _execute_command_bridge(session, root_command)


def _execute_command_bridge(session: Session, command: str):
    _, stdout, stderr = session.client.exec_command(command)

    logger.info(
        "User %s executed command %s on bridge (%s)" % (
            session.username,
            command,
            session.bridge_ip
        )
    )

    return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')


def send_file_to_bridge(session: Session, file: str, bridge_path: str):
    scp = SCPClient(session.client.get_transport())

    scp.put(file, bridge_path)

    scp.close()

    logger.info(
        "User %s sent file %s to bridge (%s)" % (
            session.username,
            file,
            session.bridge_ip
        )
    )
