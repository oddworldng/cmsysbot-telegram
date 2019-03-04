from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import CallbackQueryHandler

import helper


def start(bot, update):
    """Entry point for the menu. Replies a new message"""
    update.message.reply_text(
        text=main_menu_message(), reply_markup=main_menu_keyboard())


def build_keyboard(strings, n_cols=2, header_buttons=None,
                   footer_buttons=None):
    keyboard = [InlineKeyboardButton(s, callback_data=s) for s in strings]

    return InlineKeyboardMarkup(
        build_menu(keyboard, n_cols, header_buttons, footer_buttons))


def build_menu(buttons, n_cols=1, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def return_button(pattern):
    return [InlineKeyboardButton("Return", callback_data=pattern)]


# ##### MAIN MENU
def main_menu_message():
    return "Welcome to CmSysBot. Issue your command:"


def main_menu_keyboard():
    strings = ["Login", "Connect"]
    return build_keyboard(strings, n_cols=2)


def main_menu(bot, update):
    query = update.callback_query
    query.message.edit_text(
        text=main_menu_message(), reply_markup=main_menu_keyboard())


# ##### CONNECT MENU
def department_menu_message():
    return "Select the department:"


def department_menu_keyboard():
    strings = [o['name'] for o in helper.config['structure']]

    return build_keyboard(
        strings, n_cols=2, footer_buttons=return_button("Main"))


def department_menu(bot, update):
    query = update.callback_query
    query.message.edit_text(
        text=department_menu_message(),
        reply_markup=department_menu_keyboard())


# ##### SECTION MENU
def section_menu_message():
    return "Select your section:"


def section_menu_keyboard(selected_option):
    i = 0
    while (helper.config['structure'][i]['name'] != selected_option):
        i += 1

    strings = helper.config['structure'][i]['sections']

    return build_keyboard(
        strings, n_cols=2, footer_buttons=return_button("Connect"))


def section_menu(bot, update):
    query = update.callback_query
    selected_option = query.data

    query.message.edit_text(
        text=section_menu_message(),
        reply_markup=section_menu_keyboard(selected_option))


# ##### CONFIRM MENU
def confirm_connection_menu(bot, update):
    query = update.callback_query
    selected_option = query.data

    query.message.edit_text(selected_option)


# ##### CALLBACKS
def add_menu_callbacks(dp):
    departments_names = []
    sections_names = []

    for department in helper.config['structure']:
        departments_names.append(department['name'])
        sections_names.extend(department['sections'])

    departments_regex = "|".join(departments_names)
    sections_regex = "|".join(sections_names)

    dp.add_handler(CallbackQueryHandler(main_menu, pattern="Main"))
    dp.add_handler(CallbackQueryHandler(department_menu, pattern="Connect"))
    dp.add_handler(
        CallbackQueryHandler(section_menu, pattern=departments_regex))
    dp.add_handler(
        CallbackQueryHandler(confirm_connection_menu, pattern=sections_regex))
