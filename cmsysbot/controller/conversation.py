from telegram import Bot
from telegram.ext import ConversationHandler, Updater

from . import menu
from system import remote

# Conversation States
USERNAME, PASSWORD, SOFTWARE = range(3)


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
