"""
In this module are defined all the messages (without keyboard) returned by the
bot.
"""

import re

from utils import Computer

from .keyboard import Keyboard


def connect_output(connected: bool, bridge_ip: str) -> Keyboard:
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

    if connected:
        text = "Successfully connected to %s!" % bridge_ip
    else:
        text = ("Unable to connect to %s.\n"
                "Please try to login with different credentials!" % bridge_ip)

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
    text = "Disconnected from %s" % bridge_ip

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
    text = "Computer %s: %s --> %s" % (computer.name, last_ip, computer.ip)

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
    text = "-- [Executing %s] --" % plugin_name

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
    text = "Argument needed: %s " % argument_text

    # Keyboard
    return Keyboard(text)


def plugin_output(name: str, ip: str, plugin_name: str, stdout: str,
                  stderr: str) -> Keyboard:
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
        text += "-> [Error]: %s\n" % stderr

    # Show standard output
    if stdout:
        text += stdout

    # Can't send an empty message in telegram, so send '-> No ouptut' instead
    if not text:
        text = "-> No output"

    text = "[%s (%s) - %s]\n%s" % (name, ip, plugin_name, text)

    # Keyboard
    return Keyboard(text)
