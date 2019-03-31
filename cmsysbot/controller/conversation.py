import re

from telegram import Bot
from telegram.ext import ConversationHandler, Updater

from system import bridge, remote
from utils import State, plugins

from . import menu

# Conversation States
USERNAME, PASSWORD, SOFTWARE, ANSWER = range(4)

# ######################################################################
#                          LOGIN CONVERSATION
# ######################################################################


def start_plugin(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    plugin_name = re.search(State.START_PLUGIN, query.data).group(1)
    user_data['arguments'] = plugins.get_plugin_arguments(plugin_name)
    user_data['command'] = [plugin_name]

    return collect_arguments(bot, update, user_data)


def collect_arguments(bot: Bot, update: Updater, user_data: dict):

    session = user_data['session']

    while user_data['arguments']:
        argument = user_data['arguments'].pop(0)

        if argument == "$USERNAME":
            user_data['command'].append(session.username)

        elif argument == "$PASSWORD":
            user_data['command'].append(session.password)

        elif argument == "$TARGET_IP":
            user_data['command'].append("$TARGET_IP")

        else:
            if update.message:
                update.message.reply_text(argument)
            else:
                update.callback_query.message.reply_text(argument)

            print(argument)
            return ANSWER

    print(user_data['command'])

    return execute_plugin(bot, update, user_data)


def execute_plugin(bot: Bot, update: Updater, user_data: dict):

    session = user_data['session']

    # Check for arguments that will be repeated
    target_ip_index = -1
    try:
        target_ip_index = user_data['command'].index("$TARGET_IP")

    except ValueError:
        pass

    for computer in session.computers.get_included_computers():
        target_ip = computer.ip

        if target_ip_index != -1:
            user_data['command'][target_ip_index] = computer.ip

        print(user_data['command'])

        bridge.send_file(session.client, user_data['command'][0])

        print(
            remote.execute_script_as_root(session, target_ip,
                                          user_data['command']))


def answer(bot: Bot, update: Updater, user_data: dict) -> int:

    user_data['command'].append("\"%s\"" % update.message.text)
    print("Answer: " + update.message.text)

    return collect_arguments(bot, update, user_data)


def login(bot: Bot, update: Updater) -> int:
    """ENTRY POINT. Ask for the username and wait for the answer"""

    message = update.callback_query.message
    message.reply_text("Please introduce your username and password")
    message.reply_text("Enter your username: ")

    return USERNAME


def get_username(bot: Bot, update: Updater, user_data: dict) -> int:
    """Get the username from the last messge. Ask for the password and wait"""

    user_data['session'].username = update.message.text

    update.message.reply_text("Enter your password: ")

    return PASSWORD


def get_password(bot: Bot, update: Updater,
                 user_data: dict) -> ConversationHandler:
    """Get the password from the last message. End conversation"""

    user_data['session'].password = update.message.text

    update.message.reply_text("This credentials will be used for future \
                              commands.")

    menu.connect(bot, update, user_data)

    return ConversationHandler.END


def software(bot: Bot, update: Updater) -> int:
    """ENTRY POINT. Ask for the software to install"""

    message = update.callback_query.message
    message.reply_text("Please type software name to install")

    return SOFTWARE


def get_software(bot: Bot, update: Updater,
                 user_data: dict) -> ConversationHandler:
    """Get the software to install from user input"""

    input_software = update.message.text
    message = update.message

    # Get all necessary data for sending the command
    client = user_data['session'].client
    computers = user_data['session'].computers
    username = user_data['session'].username
    password = user_data['session'].password

    for computer in computers.get_included_computers():
        target_ip = computer.ip

        # Send the shutdown command
        remote.install_software(client, target_ip, username, password,
                                input_software)

        message.reply_text(
            "Software %s installed successfully" % input_software)

    menu.new_main(bot, update, user_data)

    return ConversationHandler.END
