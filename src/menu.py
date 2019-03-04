from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import CallbackQueryHandler

import helper


def start(bot, update):
    """Entry point for the menu. Replies a new message"""
    update.message.reply_text(
        text=main_menu_message(), reply_markup=main_menu_keyboard())


def return_button(pattern):
    return [InlineKeyboardButton("Return", callback_data=pattern)]


def build_menu(buttons, n_cols=1, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


# ##### MAIN MENU
def main_menu_message():
    return "Welcome to CmSysBot. Issue your command:"


def main_menu_keyboard():
    keyboard = [
        InlineKeyboardButton("Login", callback_data="login"),
        InlineKeyboardButton("Connect", callback_data="connect")
    ]
    return InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))


def main_menu(bot, update):
    query = update.callback_query
    query.message.edit_text(
        text=main_menu_message(), reply_markup=main_menu_keyboard())


# ##### CONNECT MENU
def connect_menu_message():
    return "Select your connection:"


def connect_menu_keyboard():
    strings = list(
        map(lambda o: o['name'], helper.config['structure']['multiple']))

    keyboard = [
        InlineKeyboardButton(s, callback_data="subsection") for s in strings
    ]

    return InlineKeyboardMarkup(
        build_menu(keyboard, n_cols=2, footer_buttons=return_button("main")))


def connect_menu(bot, update):
    query = update.callback_query
    query.message.edit_text(
        text=connect_menu_message(), reply_markup=connect_menu_keyboard())


# ##### SUBSECTION MENU
def subsection_menu_message():
    return "Select subsection:"


def subsection_menu_keyboard():
    keyboard = [InlineKeyboardButton("test", callback_data="test")]

    return InlineKeyboardMarkup(
        build_menu(
            keyboard, n_cols=2, footer_buttons=return_button("connect")))


def subsection_menu(bot, update):
    query = update.callback_query
    query.message.edit_text(
        text=subsection_menu_message(),
        reply_markup=subsection_menu_keyboard())


# ##### CALLBACKS
def add_menu_callbacks(dp):
    dp.add_handler(CallbackQueryHandler(main_menu, pattern="main"))
    dp.add_handler(CallbackQueryHandler(connect_menu, pattern="connect"))
    dp.add_handler(CallbackQueryHandler(subsection_menu, pattern="subsection"))
