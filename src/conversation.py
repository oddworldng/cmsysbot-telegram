# Conversation handler for /login
from telegram.ext import (ConversationHandler, CommandHandler,
                          CallbackQueryHandler, MessageHandler, Filters)

import helper

USERNAME, PASSWORD = range(2)


def login(bot, update):
    message = helper.getMessage(update)
    message.reply_text("Please introduce your username and password")
    message.reply_text("Enter your username: ")
    return USERNAME


def get_username(bot, update, user_data):
    user_data['username'] = update.message.text
    return ask_password(bot, update)


def ask_password(bot, update):
    update.message.reply_text("Enter your password: ")
    return PASSWORD


def get_password(bot, update, user_data):
    user_data['password'] = update.message.text
    return login_end(bot, update, user_data)


def login_end(bot, update, user_data):
    user_data['password'] = update.message.text

    update.message.reply_text("Your username: " + user_data['username'])
    update.message.reply_text("Your password: " + user_data['password'])
    update.message.reply_text("This credentials will be used for future \
                              connections.")

    return ConversationHandler.END


def add_conversation_callbacks(dp):
    login_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(login, pattern="login"),
                      CommandHandler("login", login)],
        states={
            USERNAME:
            [MessageHandler(Filters.text, get_username, pass_user_data=True)],
            PASSWORD:
            [MessageHandler(Filters.text, get_password, pass_user_data=True)],
        },
        fallbacks=[])

    dp.add_handler(login_conv_handler)
