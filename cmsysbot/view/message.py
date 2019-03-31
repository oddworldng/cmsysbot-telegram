import os
from typing import List

from utils import Computer

from .keyboard import Keyboard


def connect_output(connected: bool, bridge_ip: str) -> Keyboard:

    text = ""

    # Text
    if connected:
        text = "Successfully connected to %s!" % bridge_ip
    else:
        text = "Unable to connect to %s.\nPlease try to login with different credentials!" % bridge_ip

    # Keyboard
    return Keyboard(text)


def disconnect_output(bridge_ip: str) -> Keyboard:

    # Text
    text = "Disconnected from %s" % bridge_ip

    # Keyboard
    return Keyboard(text)


def update_ip_output(computer: Computer, last_ip: str):

    # Text
    text = "Computer %s: %s --> %s" % (computer.name, last_ip, computer.ip)

    # Keyboard
    return Keyboard(text)


# ######################################################################
#                          LOGIN CONVERSATION
# ######################################################################


def login_start() -> Keyboard:
    # Text
    text = "Please introduce your username and password"

    # Keyboard
    return Keyboard(text)


def ask_username() -> Keyboard:
    # Text
    text = "Enter your username"

    # Keyboard
    return Keyboard(text)


def ask_password() -> Keyboard:
    # Text
    text = "Enter your password"

    # Keyboard
    return Keyboard(text)


# ######################################################################
#                         PLUGIN CONVERSATION
# ######################################################################


def plugin_start(plugin_name: str):

    # Text
    text = "-- [Executing %s] --" % plugin_name

    # Keyboard
    return Keyboard(text)


def ask_argument(argument_text: str):

    # Text
    text = "Argument needed: %s " % argument_text

    # Keyboard
    return Keyboard(text)


def plugin_output(computer: Computer, plugin_name: str, stdout: str,
                  stderr: str):
    # Text
    text = ""

    if stderr:
        text += "-> [ERROR]:\n%s" % stderr

    if stdout:
        text += stdout

    if not text:
        text = "-> No output"

    text = "[%s - %s]:\n\n%s" % (computer, plugin_name, text)

    # Keyboard
    return Keyboard(text)
