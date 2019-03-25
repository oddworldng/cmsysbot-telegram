from telegram import Bot
from telegram.ext import Updater

from . import menu


def start(bot: Bot, update: Updater, user_data: dict):

    menu.new_main(bot, update, user_data)
