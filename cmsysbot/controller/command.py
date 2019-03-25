from telegram import Bot
from telegram.ext import Updater

from utils import Session

from . import menu


def start(bot: Bot, update: Updater, user_data: dict):

    if not 'session' in user_data:
        user_data['session'] = Session()

    s = user_data['session']

    menu.new_main(bot, update, user_data)
