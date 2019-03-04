from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import CallbackQueryHandler


def start(bot, update):
    """Entry point for the menu. Replies a new message"""
    update.message.reply_text(text=main_menu_message(),
                              reply_markup=main_menu_keyboard())


# ##### MAIN MENU
def main_menu_message():
    return "Welcome to CmSysBot. Issue your command:"


def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton("Login", callback_data="login")],
                [InlineKeyboardButton("Connect", callback_data="connect")]]
    return InlineKeyboardMarkup(keyboard)


def main_menu(bot, update):
    query = update.callback_query
    query.message.edit_text(
        text=main_menu_message(), reply_markup=main_menu_keyboard())


# ##### CONNECT MENU
def connect_menu_message():
    return "Select your connection:"


def connect_menu_keyboard():
    keyboard = [[InlineKeyboardButton("Test", callback_data="1")],
                [InlineKeyboardButton("Return", callback_data="main")]]

    return InlineKeyboardMarkup(keyboard)


def connect_menu(bot, update):
    query = update.callback_query
    query.message.edit_text(
        text=connect_menu_message(), reply_markup=connect_menu_keyboard())


def add_menu_callbacks(dp):
    dp.add_handler(CallbackQueryHandler(main_menu, pattern="main"))
    dp.add_handler(CallbackQueryHandler(connect_menu, pattern="connect"))
