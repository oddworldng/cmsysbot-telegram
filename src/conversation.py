from telegram.ext import (ConversationHandler,
                          CallbackQueryHandler, MessageHandler, Filters)

import menu
import helper
import main

# Conversation States
IP, USERNAME, PASSWORD = range(3)


# ##### LOGIN CONVERSATION
def login(bot, update):
    """ENTRY POINT. Ask for the username and wait for the answer"""
    message = helper.getMessage(update)
    message.reply_text("Please introduce your username and password")
    message.reply_text("Enter your username: ")
    return USERNAME


def get_username(bot, update, user_data):
    """Get the username from the last messge. Ask for the password and wait"""
    user_data['username'] = update.message.text
    update.message.reply_text("Enter your password: ")
    return PASSWORD


def get_password(bot, update, user_data):
    """Get the password from the last message. End conversation"""
    user_data['password'] = update.message.text

    update.message.reply_text("Your username: " + user_data['username'])
    update.message.reply_text("Your password: " + user_data['password'])
    update.message.reply_text("This credentials will be used for future \
                              connections.")

    main.connect(bot, update, user_data)

    return ConversationHandler.END


# ##### IP CONVERSATION
def ip(bot, update):
    """ENTRY POINT. Ask the user for an ip"""
    query = update.callback_query
    query.message.edit_text("Introduce an ip: ")
    return IP


def get_ip(bot, update, user_data):
    """Get the ip from the last message. End conversation"""
    user_data['bridge_ip'] = update.message.text

    menu.confirm_connection_menu(bot, update, user_data)

    return ConversationHandler.END


# ##### CONVERSATION CALLBACKS
def add_conversation_callbacks(dp):
    """Add all the conversation handlers to the Dispatcher"""

    # Login handler
    login_conv_handler = ConversationHandler(
        # Entry points: From InlineKeyboardButton or /login
        entry_points=[
            CallbackQueryHandler(login, pattern="^Ip-Yes$")
        ],
        states={
            USERNAME:
            [MessageHandler(Filters.text, get_username, pass_user_data=True)],
            PASSWORD:
            [MessageHandler(Filters.text, get_password, pass_user_data=True)],
        },
        fallbacks=[])

    # Ip handler
    ip_conv_handler = ConversationHandler(
        # Entry points: From InlineKeyboardButton
        entry_points=[CallbackQueryHandler(ip, pattern="^Ask-Ip$")],
        states={
            IP: [MessageHandler(Filters.text, get_ip, pass_user_data=True)]
        },
        fallbacks=[])

    dp.add_handler(login_conv_handler)
    dp.add_handler(ip_conv_handler)
