"""
Module defining useful classes and methods for representing messages on the
chat.
"""

import textwrap
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, ParseMode
from telegram.ext import Updater


def Button(text: str, callback_data: str = None) -> InlineKeyboardButton:
    """
    Alias function for creating an InlineKeyboardButton

    Args:
        text (:obj:`str`): The text label of the button
        callback_data (:obj:`str`): The string returned in
        :obj:`callback_query.data`, and that can be caught by the
        :obj:`CallbackQueryHandlers`
    """

    # If no callback_data defined, use the actual label
    if not callback_data:
        callback_data = text

    return InlineKeyboardButton(text, callback_data=callback_data)


class Keyboard:
    """
    Generator of messages that can have a :obj:`telegram.InlineKeyboard`
    attached to it.

    Note:
        It provides an easier syntax to reply and edit messages on the chat, so
        it should be used instead of :obj:`message.reply_text` and
        :obj:`message.edit_text`. For more examples, see the module
        ``view.message``

    Attributes:
        text (:obj:`str`): Text displayed on the message
        n_cols (:obj:`int`): Number of columns in which the :obj:`main_buttons`
            array should be split.
        header_buttons (:obj:`List[telegram.InlineKeyboardButton]`): List of
            buttons that are displayed on the top. Header buttons are not split
            in several columns (n_cols doesn't affect them)
        main_buttons (:obj:`List[telegram.InlineKeyboardButton]`): List of
            buttons that are displayed between the :obj:`header_buttons` and
            :obj:`footer_buttons`.
        footer_buttons (:obj:`List[telegram.InlineKeyboardButton]`): List of
            buttons that are displayed on the bottom. Footer buttons are not
            split in several columns (n_cols doesn't affect them)
    """

    def __init__(
        self,
        text: str,
        n_cols: int = 1,
        header_buttons: List[InlineKeyboardButton] = None,
        main_buttons: List[InlineKeyboardButton] = None,
        footer_buttons: List[InlineKeyboardButton] = None,
    ):
        self.text = text
        self.n_cols = n_cols
        self.header_buttons = header_buttons
        self.main_buttons = main_buttons
        self.footer_buttons = footer_buttons

    def reply(self, update: Updater, parse_mode: ParseMode = ParseMode.HTML):
        """
        Reply to the message attached to the :obj:`update`, constructing a new
        message with the defined text and buttons. Uses :obj:`_get_message` for
        extracting the message from the :obj:`update`.

        Args:
            update (:obj:`telegram.ext.update.Updater`): The Updater associated
                to the bot.
        """

        # 4096 is the max allowed length for a telegram message
        # https://core.telegram.org/method/messages.sendMessage
        wrapper = textwrap.TextWrapper(width=4096, replace_whitespace=False)

        for text_chunk in wrapper.wrap(self.text):
            self.__get_message(update).reply_text(
                text=text_chunk,
                reply_markup=self.__generate_keyboard(),
                parse_mode=parse_mode,
            )

    def edit(self, update: Updater, parse_mode: ParseMode = ParseMode.HTML):
        """
        Edit the message attached to the :obj:`update`, replacing it with the
        defined text and buttons. Uses :obj:`_get_message` for extracting the
        message from the :obj:`update`.

        Args:
            update (:obj:`telegram.ext.update.Updater`): The Updater associated
                to the bot.
        """

        self.__get_message(update).edit_text(
            text=self.text,
            reply_markup=self.__generate_keyboard(),
            parse_mode=parse_mode,
        )

    @staticmethod
    def __get_message(update: Updater) -> Message:
        """
        Get the attached message to 'update' or 'update.callback_query'. Useful
        when a function can be called from both :obj:`telegram.CommandHandler`
        and :obj:`telegram.CallbackQueryHandler`

        Args:
            update (:obj:`telegram.ext.update.Updater`): The Updater associated
                to the bot.

        Returns:
            :obj:`telegram.Message`: The last message attached to the Updater
        """

        if update.message:
            return update.message

        return update.callback_query.message

    def __generate_keyboard(self) -> InlineKeyboardMarkup:
        """
        See :obj:`_build_menu`

        Returns:
            A :obj:`telegram.InlineKeyboardMarkup` object representing the
                constructed button keyboard.
        """

        return InlineKeyboardMarkup(self.__build_menu())

    def __build_menu(self) -> List[InlineKeyboardButton]:
        """
        Returns:
            :obj:`List[telegram.InlineKeyboardButton]` with all the keyboard
            buttons following the header -> main -> footer order.
        """

        menu: List[InlineKeyboardButton] = []

        if self.main_buttons:
            menu = [
                self.main_buttons[i : i + self.n_cols]
                for i in range(0, len(self.main_buttons), self.n_cols)
            ]

        if self.header_buttons:
            for i, element in enumerate(self.header_buttons):
                menu.insert(i, [element])

        if self.footer_buttons:
            for element in self.footer_buttons:
                menu.append([element])

        return menu
