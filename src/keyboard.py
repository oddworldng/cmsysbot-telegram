from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)


def Button(text: str, callback_data: str=None) -> InlineKeyboardButton:
    """ Alias function for creating an InlineKeyboardButton """
    if not callback_data:
        callback_data = text

    return InlineKeyboardButton(text, callback_data=callback_data)


class Keyboard:
    def __init__(self,
                 message,
                 text: str,
                 n_cols=1,
                 header_buttons=None,
                 main_buttons=None,
                 footer_buttons=None):
        self.text = text
        self.n_cols = n_cols
        self.header_buttons = header_buttons
        self.main_buttons = main_buttons
        self.footer_buttons = footer_buttons

        message.reply_text(
            text=self.text, reply_markup=self._generate_keyboard())

    def _generate_keyboard(self):
        return InlineKeyboardMarkup(self._build_menu())

    def _build_menu(self):
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