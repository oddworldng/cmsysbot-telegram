"""
In this module are defined all the messages (without keyboard) returned by the
bot.
"""

import re

from cmsysbot.utils import Computer, Session

from .keyboard import Keyboard


def connect_output(session: Session) -> Keyboard:
    """
    .. code-block:: python

        # Sucessfully connected to [bridge_ip]
        #
        # or
        #
        # Unable to connect to [bridge_ip]. Please try to login with different
        # credentials.

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = ""

    if not session.is_allowed:
        text = (
            f"Oops! user {session.username} is not allowed to access "
            f"{'/'.join(session.route)}"
        )

    elif session.connected:
        text = (
            f"Successfully connected to {session.bridge_ip}!\n\n"
            f"Now, the bot will check if the bridge computer is ready.\n\n"
            f"This action may take a few minutes if its the first time that this "
            f"computer is being used as a bridge."
        )
    else:
        text = (
            f"Unable to connect to {session.bridge_ip}.\n"
            "Please try to login with different credentials!"
        )

    # Keyboard
    return Keyboard(text)


def disconnect_output(bridge_ip: str) -> Keyboard:
    """
    .. code-block:: python

        # Disconnected from [bridge_ip]

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = f"Disconnected from {bridge_ip}"

    # Keyboard
    return Keyboard(text)


def update_ip_output(computer: Computer, last_ip: str) -> Keyboard:
    """
    .. code-block:: python

        # Computer [name]: [last_ip] -> [new_ip]

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = f"Computer {computer.name}: {last_ip} --> {computer.ip}"

    # Keyboard
    return Keyboard(text)


# ######################################################################
#                          LOGIN CONVERSATION
# ######################################################################


def login_start() -> Keyboard:
    """
    .. code-block:: python

        # Please introduce your username and password

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = "Please introduce your username and password"

    # Keyboard
    return Keyboard(text)


def ask_username() -> Keyboard:
    """
    .. code-block:: python

        # Enter your username

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = "Enter your username"

    # Keyboard
    return Keyboard(text)


def ask_password() -> Keyboard:
    """
    .. code-block:: python

        # Enter your password

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = "Enter your password"

    # Keyboard
    return Keyboard(text)


# ######################################################################
#                         PLUGIN CONVERSATION
# ######################################################################


def plugin_start(plugin_name: str) -> Keyboard:
    """
    .. code-block:: python

        # -- [Executing [plugin-name]] --

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = f"-- [Executing {plugin_name}] --"

    # Keyboard
    return Keyboard(text)


def ask_argument(argument_text: str) -> Keyboard:
    """
    .. code-block:: python

        # Argument needed: [argument-text]

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = f"Argument needed: {argument_text}"

    # Keyboard
    return Keyboard(text)


def plugin_output(
    name: str, ip: str, plugin_name: str, stdout: str, stderr: str, hide_header=False
) -> Keyboard:
    """
    .. code-block:: python

        # -> [Error]: stderr     {Doesn't show if stderr is empty}
        # stdout
        #
        #   or
        #
        # -> No output          {Shown only if stderr and stdout are emtpy

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = ""

    # Remove "[sudo] password for X:" prompt"
    stderr = re.sub(r"\[sudo\].*?:", "", stderr).strip()

    # Show error output
    if stderr:
        text += f"-> [Error]: {stderr}\n"

    # Show standard output
    if stdout:
        text += stdout

    # Can't send an empty message in telegram, so send '-> No ouptut' instead
    if not text:
        text = "-> No output"

    header_text = f"[{name} ({ip}) - {plugin_name}]\n\n"

    text = f"{header_text if not hide_header else ''}{text}"

    # Keyboard
    return Keyboard(text)


# ######################################################################
#                       ADD COMPUTER CONVERSATION
# ######################################################################


def add_computer_start() -> Keyboard:

    # Text
    text = (
        f"Please, send a message with the data of the new computer following this "
        f"format:\n\n\tname/ip/mac\n\nOr, write 'ifconfig' on the computer and "
        f"send a picture of the output."
    )

    # Keyboard
    return Keyboard(text)


def read_inet_image(ip: str, mac: str) -> Keyboard:

    # Text
    text = (
        f"Could extract the following data from the image:"
        f"\n\n\t/{ip}/{mac}\n\nSend another image or copy the data and complete it."
    )

    # Keyboard
    return Keyboard(text)
