from utils import Session


def run(session: Session, target_ip: str, command: str):

    return _execute_command_remote(session, target_ip, command)


def run_as_root(session: Session, target_ip: str, command: str):

    root_command = "echo %s | sudo -kS %s" % (session.password, command)

    return _execute_command_remote(session, target_ip, root_command)


def _execute_command_remote(session: Session, target_ip: str, command: str):

    full_command = (
        " sshpass -p %(password)s ssh -o ConnectTimeout=3 %(username)s@%(target_ip)s \'%(command)s\'"
        % {
            'password': session.password,
            'username': session.username,
            'target_ip': target_ip,
            'command': command
        })

    _, stdout, stderr = session.client.exec_command(full_command)

    print("User %s executed comand %s on %s" % (session.username, command,
                                                target_ip))

    return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')


def send_file_to_remote(session: Session, target_ip: str, file: str,
                        remote_path: str):

    full_command = " sshpass -p %(password)s scp %(file)s %(target_ip)s:%(remote_path)s" % {
        'password': session.password,
        'target_ip': target_ip,
        'file': file,
        'remote_path': remote_path
    }

    print("User %s sent file %s from %s to %s" %
          (session.username, file, session.bridge_ip, target_ip))

    session.client.exec_command(full_command)
