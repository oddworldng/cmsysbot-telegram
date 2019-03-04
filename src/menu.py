from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import CallbackQueryHandler


# ################## MENUS ###################
def main_menu_message():
    return "Welcome to CmSysBot. Issue your command:"


def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton("Login", callback_data="login")]]
    return InlineKeyboardMarkup(keyboard)


def main_menu(bot, update):
    update.message.reply_text(
        text=main_menu_message(), reply_markup=main_menu_keyboard())


def add_menu_callbacks(dp):
    dp.add_handler(CallbackQueryHandler(main_menu, pattern="main"))
