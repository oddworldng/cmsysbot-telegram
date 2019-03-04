import argparse
import logging
import subprocess

import paramiko

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler,
                          CallbackQueryHandler)

import menu
import helper

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

USERNAME, PASSWORD = range(2)

# Variable holding the JSON file
config = None


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Show the main menu when the command /start is issued."""
    menu.main_menu(bot, update)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def run(bot, update, args):
    result = subprocess.run(list(args), stdout=subprocess.PIPE)
    update.message.reply_text(result.stdout.decode('utf-8'))


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


# Login functions
def login(bot, update):
    message = helper.getMessage(update)
    message.reply_text("Please introduce your username and password")
    message.reply_text("Enter your username: ")
    return USERNAME


def get_username(bot, update, user_data):
    user_data['username'] = update.message.text
    return ask_password(bot, update)


def ask_password(bot, update):
    update.message.reply_text("Enter your password: ")
    return PASSWORD


def get_password(bot, update, user_data):
    user_data['password'] = update.message.text
    return login_end(bot, update, user_data)


def login_end(bot, update, user_data):
    user_data['password'] = update.message.text

    update.message.reply_text("Your username: " + user_data['username'])
    update.message.reply_text("Your password: " + user_data['password'])
    update.message.reply_text("This credentials will be used for future \
                              connections.")

    return ConversationHandler.END


# Execute command as root
def run_as_root(bot, update, user_data, args):

    if 'client' in user_data:

        # Variables
        client = user_data['client']
        password = user_data['password']

        # Run as root
        arguments = " ".join(args)
        command = ' printf "' + password + '\\n" | sudo --stdin ' + arguments
        stdin, stdout, stderr = client.exec_command(command)

        # Output
        output_message = stdout.read().decode('utf-8')
        update.message.reply_text(output_message)


# Connection functions
def connect(bot, update, user_data, args):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy)

    client.connect(args[0], 22, user_data['username'], user_data['password'])
    update.message.reply_text("Sucessfully connected to " + args[0] + "!\n" +
                              "To run commands in remote use /rrun [command]")

    user_data['client'] = client


def remote_run(bot, update, user_data, args):
    if 'client' in user_data:
        print("Executing: " + " ".join(args))

        client = user_data['client']
        stdin, stdout, stderr = client.exec_command(" ".join(args))

        output_message = stdout.read().decode('utf-8')
        update.message.reply_text(output_message)
    else:
        update.message.reply_text("Start a connection first with /connect")


# ################## MAIN  ###################
def main():
    # Parse arguments from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="JSON file with the Bot Configuration")
    args = parser.parse_args()

    # Open the config.json file
    global config
    config = helper.open_json_file(args.config)

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(config['token'])
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("run", run, pass_args=True))
    dp.add_handler(
        CommandHandler(
            "connect", connect, pass_user_data=True, pass_args=True))
    dp.add_handler(
        CommandHandler(
            "sudo", run_as_root, pass_user_data=True, pass_args=True))
    dp.add_handler(
        CommandHandler(
            "rrun", remote_run, pass_user_data=True, pass_args=True))

    # Conversation handler for /login
    login_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(login, pattern="login"),
                      CommandHandler("login", login)],
        states={
            USERNAME:
            [MessageHandler(Filters.text, get_username, pass_user_data=True)],
            PASSWORD:
            [MessageHandler(Filters.text, get_password, pass_user_data=True)],
        },
        fallbacks=[RegexHandler('^Done$', login_end)])
    dp.add_handler(login_conv_handler)

    # Add all menu callbacks
    menu.add_menu_callbacks(dp)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    print("Bot started! Running...")
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
