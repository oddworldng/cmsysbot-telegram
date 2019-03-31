import os
import re

from telegram import Bot, ChatAction
from telegram.ext import ConversationHandler, Updater

import view
from system import Plugin, bridge
from utils import Session, State, send_action, states

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
    user_data['plugin'] = Plugin(plugin_path_server)

    print("Plugin name: " + user_data['plugin'].name)
    print("Route in server: " + plugin_path_server)

    return collect_arguments(bot, update, user_data)


def collect_arguments(bot: Bot, update: Updater, user_data: dict):

    session = user_data['session']

    plugin = user_data['plugin']
    plugin.fill_session_arguments(session)

    for argument in plugin.arguments:
        if argument[0] != '$' and not plugin.arguments[argument]:
            user_data['asking_for'] = argument
            view.ask_argument(argument).reply(update)
            return ANSWER

    print(user_data['plugin'].arguments)

    return execute_plugin(bot, update, user_data=user_data)


@send_action(ChatAction.TYPING)
def execute_plugin(bot: Bot, update: Updater, user_data: dict):

    session: Session = user_data['session']
    plugin: Plugin = user_data['plugin']

    bridge_plugin_path = "%s/%s" % (states.config_file.bridge_tmp_dir,
                                    plugin.name)
    bridge.send_file_to_bridge(session, plugin.path, bridge_plugin_path)
    plugin.path = bridge_plugin_path

    print(plugin.path)

    for computer in session.computers.get_included_computers():

        stdout, stderr = plugin.run(session, computer)
        view.plugin_output(computer, plugin.name, stdout, stderr).reply(update)

    menu.new_main(bot, update, user_data)


def get_answer(bot: Bot, update: Updater, user_data: dict) -> int:

    argument = user_data['asking_for']
    user_data['plugin'][argument] = update.message.text
    print("Answer: " + update.message.text)

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

    user_data['session'].username = update.message.text

    view.ask_password().reply(update)

    return PASSWORD


def get_password(bot: Bot, update: Updater,
                 user_data: dict) -> ConversationHandler:
    """Get the password from the last message. End conversation"""

    user_data['session'].password = update.message.text

    menu.connect(bot, update, user_data)

    return ConversationHandler.END
