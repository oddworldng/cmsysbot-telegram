import logging

from telegram.ext import Updater
from telegram.error import InvalidToken

from utils import config_json
from controller import controller
import re

import helper

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Load the config file
    helper.config = config_json.Config(helper.DEFAULT_CONFIG_FILEPATH)

    content = re.search("include-(.*)", "include-all").group(1)
    print(content)

    # Create the EventHandler and pass it your bot's token.
    try:
        updater = Updater(helper.config.token)
    except InvalidToken:
        print("Invalid Token! Please check your token in the config.json file")
        return

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add all callbacks
    controller.add_callbacks(dp)
    controller.add_command_callbacks(dp)
    controller.add_conversation_callbacks(dp)

    # Enable error loggin
    dp.add_error_handler(error)

    # Start the bot!!
    print("%s started! Running..." % helper.config.name)
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()