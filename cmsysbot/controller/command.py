"""
In this module are defined all the ``command`` :obj:`callbacks` used by the
bot.

Note:
    A :obj:`command` is any function that is called when sending a
    :obj:`/command` to the bot
"""

from telegram import Bot
from telegram.ext import Updater

from cmsysbot.utils import Session

from . import menu


def start(bot: Bot, update: Updater, user_data: dict):
    """
    Start the bot. Command called when connecting the first time. Creates a
    new session if necessary.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    if "session" not in user_data:
        user_data["session"] = Session()

    # Show the main menu on a new message
    menu.new_main(bot, update, user_data)
