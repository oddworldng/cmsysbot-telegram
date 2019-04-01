import os
import re

from telegram import Bot, ChatAction
from telegram.ext import ConversationHandler, Updater
from telegram.ext.dispatcher import run_async

import view
from system import Plugin, PluginVar, bridge, remote
from utils import Computer, Session, State, states

from . import general, menu

# Conversation States
USERNAME, PASSWORD, ANSWER = range(3)

# ######################################################################
#                         PLUGIN CONVERSATION
# ######################################################################


def start_plugin_from_callback(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    # Plugin path in server
    plugin_path_server = re.search(State.START_PLUGIN, query.data).group(1)

    user_data['plugin'] = Plugin(plugin_path_server)

    view.plugin_start(user_data['plugin'].name).edit(update)

    return collect_arguments(bot, update, user_data)


def start_plugin_from_download(bot: Bot, update: Updater, user_data: dict):

    session = user_data['session']
    message = update.message

    if not session.connected:
        message.reply_text(
            "You must be connected to a bridge computer before sending files!")
        return ConversationHandler.END

    # Download the file
    file_object = message.document.get_file()
    download_path = "%s/%s" % (states.config_file.server_tmp_dir,
                               message.document.file_name)

    file_object.download(download_path)

    # Make downloaded file executable by the user
    os.chmod(download_path, 0o764)

    user_data['plugin'] = Plugin(download_path)

    view.plugin_start(user_data['plugin'].name).reply(update)

    return collect_arguments(bot, update, user_data)


def collect_arguments(bot: Bot, update: Updater, user_data: dict):

    session = user_data['session']

    plugin = user_data['plugin']
    plugin.fill_session_arguments(session)

    for argument in plugin.arguments:
        if argument[0] != '$' and not plugin.arguments[argument]:
            user_data['ask_argument'] = argument
            view.ask_argument(argument).reply(update)
            return ANSWER

    return execute_plugin(bot, update, user_data=user_data)


def execute_plugin(bot: Bot, update: Updater, user_data: dict):

    session: Session = user_data['session']
    plugin: Plugin = user_data['plugin']

    # Get route in bridge
    bridge_plugin_path = "%s/%s" % (states.config_file.bridge_tmp_dir,
                                    plugin.name)
    # Send plugin to bridge
    bridge.send_file_to_bridge(session, plugin.path, bridge_plugin_path)

    if plugin.source == PluginVar.SOURCE_BRIDGE:
        command = "%s %s" % (bridge_plugin_path, " ".join(
            plugin.arguments.values()))

        print("bridge: %s" % command)

        computer = Computer({
            "name": "Bridge",
            "ip": session.bridge_ip,
            "mac": ""
        })

        stdout = ""
        stderr = ""
        if plugin.root:
            stdout, stderr = bridge.run_as_root(session, command)
        else:
            stdout, stderr = bridge.run(session, command)

        view.plugin_output(computer, plugin.name, stdout, stderr).reply(update)

    else:
        bot.send_chat_action(
            chat_id=update.message.chat_id, action=ChatAction.TYPING)
        for computer in session.computers.get_included_computers():

            remote_plugin_path = "%s/%s" % (states.config_file.remote_tmp_dir,
                                            plugin.name)

            # Send plugin to remote for execution
            remote.send_file_to_remote(session, computer.ip,
                                       bridge_plugin_path, remote_plugin_path)
            plugin.fill_computer_arguments(computer)

            command = "%s %s" % (remote_plugin_path, " ".join(
                plugin.arguments.values()))

            print("remote: %s" % command)

            run_plugin_remote(computer, update, session, plugin, command)

    menu.new_main(bot, update, user_data)

    return ConversationHandler.END


@run_async
def run_plugin_remote(computer, update: Updater, session: Session, plugin,
                      command: str):
    stdout = ""
    stderr = ""
    if plugin.root:
        stdout, stderr = remote.run_as_root(session, computer.ip, command)
    else:
        stdout, stderr = remote.run(session, computer.ip, command)

    print("Stdout: %s" % stdout)
    print("Stderr: %s" % stderr)
    view.plugin_output(computer, plugin.name, stdout, stderr).reply(update)


def get_answer(bot: Bot, update: Updater, user_data: dict) -> int:

    argument = user_data['ask_argument']
    user_data['plugin'][argument] = "\"%s\"" % update.message.text

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

    general.connect(bot, update, user_data)

    return ConversationHandler.END
