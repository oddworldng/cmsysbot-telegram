"""
In this module are defined all the ``conversations`` used by the bot.

Note:
    A ``conversation`` is a type of interaction between the user and the bot
    based on a "Question-Answer" system. It can also be represented as a state
    machine.
"""

import os
import re

import pytesseract
from telegram import Bot
from telegram.ext import ConversationHandler, Updater

from cmsysbot import view
from cmsysbot.system import Plugin
from cmsysbot.utils import Session, State, states
from cmsysbot.utils.decorators import connected, not_connected

from . import general, menu

try:
    from PIL import Image
except ImportError:
    import Image


# Conversation States
USERNAME, PASSWORD, ANSWER, INET_IMAGE = range(4)

# ######################################################################
#                         PLUGIN CONVERSATION
# ######################################################################


@connected
def start_plugin_from_callback(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    # Plugin path in server
    plugin_path_server = re.search(State.START_PLUGIN, query.data).group(1)

    user_data["plugin"] = Plugin(plugin_path_server)

    view.plugin_start(user_data["plugin"].name).edit(update)

    return collect_arguments(bot, update, user_data)


@connected
def start_plugin_from_download(bot: Bot, update: Updater, user_data: dict):

    session = Session.get_from(user_data)
    message = update.message

    if not session.connected:
        message.reply_text(
            "You must be connected to a bridge computer before sending files!"
        )
        return ConversationHandler.END

    # Download the file
    file_object = message.document.get_file()
    download_path = f"{states.config_file.server_tmp_dir}/{message.document.file_name}"

    file_object.download(download_path)

    # Make downloaded file executable by the user
    os.chmod(download_path, 0o764)

    user_data["plugin"] = Plugin(download_path)

    view.plugin_start(user_data["plugin"].name).reply(update)

    return collect_arguments(bot, update, user_data)


@connected
def collect_arguments(bot: Bot, update: Updater, user_data: dict):

    session = Session.get_from(user_data)

    plugin = user_data["plugin"]
    plugin.fill_session_arguments(session)

    for argument in plugin.arguments:
        if argument[0] != "$" and not plugin.arguments[argument]:
            user_data["ask_argument"] = argument
            view.ask_argument(argument).reply(update)
            return ANSWER

    return execute_plugin(bot, update, user_data=user_data)


@connected
def execute_plugin(bot: Bot, update: Updater, user_data: dict):

    session = Session.get_from(user_data)
    plugin: Plugin = user_data["plugin"]

    for name, ip, stdout, stderr in plugin.run(session):
        view.plugin_output(name, ip, plugin.name, stdout, stderr).reply(update)

    menu.new_main(bot, update, user_data)

    return ConversationHandler.END


@connected
def get_answer(bot: Bot, update: Updater, user_data: dict) -> int:

    argument = user_data["ask_argument"]
    user_data["plugin"][argument] = f'"{update.message.text}"'

    return collect_arguments(bot, update, user_data)


# ######################################################################
#                          LOGIN CONVERSATION
# ######################################################################


def login(bot: Bot, update: Updater) -> int:
    """ENTRY POINT. Ask for the username and wait for the answer"""

    view.login_start().reply(update)
    view.ask_username().reply(update)

    return USERNAME


def get_username(bot: Bot, update: Updater, user_data: dict) -> int:
    """Get the username from the last messge. Ask for the password and wait"""

    Session.get_from(user_data).username = update.message.text

    view.ask_password().reply(update)

    return PASSWORD


def get_password(bot: Bot, update: Updater, user_data: dict) -> ConversationHandler:
    """Get the password from the last message. End conversation"""

    Session.get_from(user_data).password = update.message.text

    general.connect(bot, update, user_data)

    return ConversationHandler.END


# ######################################################################
#                       ADD COMPUTER CONVERSATION
# ######################################################################


def add_computer(bot: Bot, update: Updater, user_data: dict) -> int:
    view.add_computer_start().reply(update)

    return INET_IMAGE


def inet_image(bot: Bot, update: Updater) -> int:

    photo_file = update.message.photo[-1].get_file()

    download_path = f"{states.config_file.server_tmp_dir}/inet_config.jpg"
    photo_file.download(download_path)

    text = pytesseract.image_to_string(Image.open(download_path))

    print(text)

    IP_REGEX = re.compile(r"inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b")

    # TODO: Handle "no match" cases
    ip = IP_REGEX.search(text).group(1)

    MAC_REGEX = re.compile(r"ether\s+(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})\b")

    # TODO: Handle "no match" cases
    mac = MAC_REGEX.search(text).group(1)

    view.read_inet_image(ip, mac).reply(update)

    return INET_IMAGE


def end_add_computer(bot: Bot, update: Updater, user_data: dict) -> int:

    data = update.message.text

    name, ip, mac = data.split("/")

    print(f"New computer:\nName: {name}\nIp: {ip}\nMac: {mac}")

    # TODO: Check if ip/mac are correct

    return ConversationHandler.END
