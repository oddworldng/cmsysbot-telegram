import os
import re

from telegram import Bot
from telegram.ext import ConversationHandler, Updater

from system import bridge
from utils import State, plugins, states
from view import view

from . import menu

# Conversation States
USERNAME, PASSWORD, ANSWER = range(3)

# ######################################################################
#                         PLUGIN CONVERSATION
# ######################################################################


def start_plugin(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    # Plugin path in server
    plugin_path_server = re.search(State.START_PLUGIN, query.data).group(1)

    plugin_name = os.path.basename(plugin_path_server)

    # Plugin path in bridge
    plugin_path_bridge = "%s/%s" % (states.config_file.bridge_tmp_dir,
                                    plugin_name)

    print("Plugin name: " + plugin_name)
    print("Route in server: " + plugin_path_server)
    print("Route in bridge: " + plugin_path_bridge)

    session = user_data['session']

    # Download plugin from server to bridge
    bridge.send_file_to_bridge(session, plugin_path_server, plugin_path_bridge)

    # Plugin will store the plugin command
    user_data['plugin'] = [plugin_path_bridge]

    # Arguments will store the arguments still to be replaced
    user_data['arguments'] = plugins.get_plugin_arguments(plugin_path_server)

    return collect_arguments(bot, update, user_data)


def collect_arguments(bot: Bot, update: Updater, user_data: dict):

    session = user_data['session']

    while user_data['arguments']:
        argument = user_data['arguments'].pop(0)

        if argument == "$USERNAME":
            user_data['plugin'].append(session.username)

        elif argument == "$PASSWORD":
            user_data['plugin'].append(session.password)

        elif argument == "$TARGET_IP":
            user_data['plugin'].append("$TARGET_IP")

        else:
            if update.message:
                update.message.reply_text(argument)
            else:
                update.callback_query.message.reply_text(argument)

            print(argument)
            return ANSWER

    # Whole plugin command
    print(user_data['plugin'])

    return execute_plugin(bot, update, user_data)


def execute_plugin(bot: Bot, update: Updater, user_data: dict):

    session = user_data['session']

    for computer in session.computers.get_included_computers():
        target_ip = computer.ip

        plugin = user_data['plugin']

        output = bridge.run_plugin_in_remote_as_root(session, target_ip,
                                                     plugin)

        view.command_output(computer, plugin, output).reply(update)


def get_answer(bot: Bot, update: Updater, user_data: dict) -> int:

    user_data['plugin'].append("\"%s\"" % update.message.text)
    print("Answer: " + update.message.text)

    return collect_arguments(bot, update, user_data)


# ######################################################################
#                          LOGIN CONVERSATION
# ######################################################################


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
