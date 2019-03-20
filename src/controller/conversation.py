from telegram.ext import (ConversationHandler)

import helper

from controller import menu, callback
from states import State

# Conversation States
USERNAME, PASSWORD = range(2)


# ######################################################################
#                          LOGIN CONVERSATION
# ######################################################################
def login(bot, update):
    """ENTRY POINT. Ask for the username and wait for the answer"""
    message = helper.getMessage(update)
    message.reply_text("Please introduce your username and password")
    message.reply_text("Enter your username: ")

    return USERNAME


def get_username(bot, update, user_data):
    """Get the username from the last messge. Ask for the password and wait"""
    user_data['session'].username = update.message.text

    update.message.reply_text("Enter your password: ")

    return PASSWORD


def get_password(bot, update, user_data):
    """Get the password from the last message. End conversation"""
    user_data['session'].password = update.message.text

    update.message.reply_text("This credentials will be used for future \
                              commands.")

    callback.connect(bot, update, user_data)

    return ConversationHandler.END


# ######################################################################
#                            CALLBACKS
# ######################################################################
