# Default path in the filesystem where the config.json is located
DEFAULT_CONFIG_FILEPATH = "config/config.json"

# Singleton variable holding the JSON file (config.json)
config = None


# ######################################################################
#                         TELEGRAM FUNCTIONS
# ######################################################################
def getMessage(update):
    """
    Get the last message from 'update' or 'update.callback_query' Useful when a
    callback is called from both CommandHandler and CallbackQueryHandler
    """
    if (update.message):
        return update.message
    else:
        return update.callback_query.message
