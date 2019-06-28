from functools import wraps

from telegram import Bot, ChatAction
from telegram.ext import Updater

from cmsysbot.controller import menu

from . import Session


def connected(fun):
    @wraps(fun)
    def wrapper(bot: Bot, update: Updater, user_data, *args):
        if Session.get_from(user_data).connected:
            return fun(bot, update, user_data, *args)

        return menu.main(bot, update, user_data, *args)

    return wrapper


def not_connected(fun):
    @wraps(fun)
    def wrapper(bot: Bot, update: Updater, user_data, *args):
        if not Session.get_from(user_data).connected:
            return fun(bot, update, user_data, *args)

        return menu.main(bot, update, user_data, *args)

    return wrapper


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update, *_ = args
            bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action
            )

            return func(*args, **kwargs)

        return command_func

    return decorator


send_typing_action = send_action(ChatAction.TYPING)
