from functools import wraps

from telegram import Bot
from telegram.ext import Updater

from cmsysbot.controller import menu

from . import Session


def connected(fun):
    @wraps(fun)
    def wrapper(bot: Bot, update: Updater, user_data):
        if Session.get_from(user_data).connected:
            return fun(bot, update, user_data)
        else:
            menu.main(bot, update, user_data)

    return wrapper


def not_connected(fun):
    @wraps(fun)
    def wrapper(bot: Bot, update: Updater, user_data):
        if not Session.get_from(user_data).connected:
            return fun(bot, update, user_data)
        else:
            menu.main(bot, update, user_data)

    return wrapper
