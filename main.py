from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler)

import paramiko
import logging
import subprocess
import sys

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

USERNAME, PASSWORD = range(2)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


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
    update.message.reply_text("Please introduce your username and password")
    return ask_username(bot, update)


def ask_username(bot, update):
    update.message.reply_text("Enter your username: ")
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


# Connection functions
def connect(bot, update, user_data, args):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy)

    client.connect(args[0], 22, user_data['username'], user_data['password'])
    update.message.reply_text("Sucessfully connected to " + args[0] + "!\n"
                              + "To run commands in remote use /rrun [command]")

    user_data['client'] = client


def remote_run(bot, update, user_data, args):
    if ('client' in user_data):
        print("Executing: " + " ".join(args))

        client = user_data['client']
        stdin, stdout, stderr = client.exec_command(" ".join(args))

        output_message = stdout.read().decode('utf-8')
        update.message.reply_text(output_message)
    else:
        update.message.reply_text("Start a connection first with /connect")


def main():
    if (len(sys.argv) != 2):
        print("Use: main.py TOKEN.txt")
        return

    # Read the file and get the TOKEN as first line as first line
    token = ""

    try:
        with open(sys.argv[1], 'r') as my_file:
            token = my_file.read().splitlines()[0]
    except FileNotFoundError:
        print("File  " + sys.argv[1] + "  does not exist or can't be opened: ",
              "\nCreate a TOKEN.txt file and put your Telegram Bot Token as",
              "the first line")
        return

    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("run", run, pass_args=True))
    dp.add_handler(CommandHandler("connect", connect, pass_user_data=True, pass_args=True))
    dp.add_handler(CommandHandler("rrun", remote_run, pass_user_data=True, pass_args=True))

    # Conv handler for /login
    login_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],

        states={
            USERNAME: [MessageHandler(Filters.text,
                                      get_username,
                                      pass_user_data=True)],
            PASSWORD: [MessageHandler(Filters.text,
                                      get_password,
                                      pass_user_data=True)],
        },

        fallbacks=[RegexHandler('^Done$', login_end)]
    )

    dp.add_handler(login_conv_handler)

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
