from telegram.error import InvalidToken
from telegram.ext import Updater

from . import controller
from cmsysbot.system import log
from cmsysbot.utils import Config, states


# Error handlers also receive the raised TelegramError object in error.
def error(bot, update, error):
    """Log Errors caused by Updates."""
    log.getLogger().error('Update "%s" caused error "%s"', update, error)


def main():
    # Load the config file
    states.config_file = Config("config/config.json")

    # Initial logger config
    log.generate_log_config()

    # Create the EventHandler and pass your bot's token.
    try:
        updater = Updater(states.config_file.token)
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
    print("%s started! Running..." % states.config_file.bot_name)
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
