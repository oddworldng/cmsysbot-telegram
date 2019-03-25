from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater


def Button(text: str, callback_data: str = None) -> InlineKeyboardButton:
    """ Alias function for creating an InlineKeyboardButton """

    if not callback_data:
        callback_data = text

    return InlineKeyboardButton(text, callback_data=callback_data)


class Keyboard:
    def __init__(self,
                 text: str,
                 n_cols: int = 1,
                 header_buttons: List[InlineKeyboardButton] = None,
                 main_buttons: List[InlineKeyboardButton] = None,
                 footer_buttons: List[InlineKeyboardButton] = None):
        self.text = text
        self.n_cols = n_cols
        self.header_buttons = header_buttons
        self.main_buttons = main_buttons
        self.footer_buttons = footer_buttons

    def reply(self, update: Updater):
        self._getMessage(update).reply_text(
            text=self.text, reply_markup=self._generate_keyboard())

    def edit(self, update: Updater):
        self._getMessage(update).edit_text(
            text=self.text, reply_markup=self._generate_keyboard())

    def _getMessage(self, update: Updater) -> str:
        """
        Get the last message from 'update' or 'update.callback_query' Useful when a
        callback is called from both CommandHandler and CallbackQueryHandler
        """

        if (update.message):
            return update.message
        else:
            return update.callback_query.message

    def _generate_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(self._build_menu())

    def _build_menu(self) -> List[InlineKeyboardButton]:
        menu = []

        if self.main_buttons:
            menu = [
                self.main_buttons[i:i + self.n_cols]
                for i in range(0, len(self.main_buttons), self.n_cols)
            ]

        if self.header_buttons:
            for i, element in enumerate(self.header_buttons):
                menu.insert(i, [element])

        if self.footer_buttons:
            for element in self.footer_buttons:
                menu.append([element])

        return menu
