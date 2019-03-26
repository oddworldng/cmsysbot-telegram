from telegram import Bot
from telegram.ext import ConversationHandler, Updater

from . import menu

# Conversation States
USERNAME, PASSWORD = range(2)


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
