from telegram.ext import Updater

# TODO: Remove
def getMessage(update: Updater):
    """
    Get the last message from 'update' or 'update.callback_query' Useful when a
    callback is called from both CommandHandler and CallbackQueryHandler
    """
    if update.message:
        return update.message
    else:
        return update.callback_query.message
