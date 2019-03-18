import argparse
import logging
import subprocess
import re

import paramiko

from telegram.error import (InvalidToken)
from telegram.ext import (Updater, CommandHandler)
from wakeonlan import send_magic_packet

import conversation
import menu
import helper

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update, user_data):
    """Open a new menu when the command /start is issued."""
    menu.new_menu(bot, update, user_data)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def wake_on_lan_command(bot, update, args):
    for mac in args:
        send_magic_packet(mac)
        helper.getMessage(update).reply_text(
            'Waking up computer (MAC: ' + mac + ') ...')


def wake_on_lan_callback(bot, update, user_data):
    macs = list(user_data['computers'].get_macs())
    wake_on_lan_command(bot, update, macs)


def shutdown_computers_callback(bot, update, user_data):
    if 'client' in user_data:
        for ip in user_data['computers'].get_ips():
            if ip == user_data['ip']:  # Don't shutdown your computer!
                continue

            message = "Shutting down computer with ip %s" % ip
            update.callback_query.message.reply_text(message)

            send_command_to_client(bot, update, user_data, [ip, ['init 0']])


def update_ips(bot, update, user_data):
    if 'client' in user_data:
        client = user_data['client']
        password = user_data['password']

        get_submask_command = "ip -o -f inet addr show | awk '/scope global/ {print $4}'"
        stdin, stdout, stderr = client.exec_command(get_submask_command)
        submask = stdout.read().decode('utf-8')

        arp_scan_command = " echo " + password + " | sudo -S arp-scan " + submask
        stdin, stdout, stderr = client.exec_command(arp_scan_command)

        dictionary = {}
        for line in stdout:
            ip_and_mac = re.search(
                '((?:\d{1,3}\.){3}\d{1,3}).*((?:\w\w:){5}\w\w)', line)

            if ip_and_mac is not None:
                ip = ip_and_mac.group(1)
                mac = ip_and_mac.group(2)
                dictionary[mac] = ip

        print(dictionary)

        for computer in user_data['computers'].get_computers():
            if computer.mac in dictionary:
                computer.ip = dictionary[computer.mac]
                message = 'Ip for computer with mac %s updated to %s' % (
                    computer.mac, computer.ip)
                update.callback_query.message.reply_text(message)
                print(message)

        user_data['computers'].save()


def send_command_to_client(bot, update, user_data, args):

    # Get arguments
    try:
        ip = args[0]
        input_command = " ".join(args[1])
    except IndexError:
        update.message.reply_text(
            "Wrong command. Please use /send <ip> <command>.")

    if 'client' in user_data:

        # Variables
        client = user_data['client']
        username = user_data['username']
        password = user_data['password']

        # Run as root
        output_command = " sshpass -p " + password + " ssh " + username + "@" + ip + " 'echo " + password + " | sudo -S " + input_command + "'"
        stdin, stdout, stderr = client.exec_command(output_command)
        print(output_command)

        # Output
        output_message = stdout.read().decode('utf-8')
        print(output_message)
        # update.message.reply_text(output_message)


def run(bot, update, args):
    """"Execute a *nix command in the machine where the bot is hosted."""
    result = subprocess.run(list(args), stdout=subprocess.PIPE)
    update.message.reply_text(result.stdout.decode('utf-8'))


def run_as_root(bot, update, user_data, args):
    """Promote user to root and execute command"""

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


def connect(bot, update, user_data):
    """
    Establish a SSH connection from the bot machine to the bridge computer
    """
    try:
        # Start Paramiko and setup SSH configuration
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)

        # Try to connect to the client
        client.connect(user_data['temp_ip'], 22, user_data['temp_username'],
                       user_data['temp_password'])

        # Success!! Save all the temporal user paramenters
        user_data['client'] = client
        user_data['username'] = user_data['temp_username']
        user_data['password'] = user_data['temp_password']
        user_data['ip'] = user_data['temp_ip']
        if 'temp_route' in user_data:
            user_data['route'] = user_data['temp_route']
        if 'temp_computers' in user_data:
            user_data['computers'] = user_data['temp_computers']

        # Return a successful connection message
        update.message.reply_text(
            "Sucessfully connected to " + user_data['temp_ip'] + "!\n" +
            "To run commands in remote use /rrun [command]")

    except paramiko.AuthenticationException as error:
        update.message.reply_text(
            str(error) + " Please try to login with different credentials!")

    finally:
        menu.new_menu(bot, update, user_data)


def remote_run(bot, update, user_data, args):
    """
    Run a *nix command in the bridge computer
    """
    if 'client' in user_data:
        print("Executing: " + " ".join(args))

        client = user_data['client']
        stdin, stdout, stderr = client.exec_command(" ".join(args))

        output_message = stdout.read().decode('utf-8')
        update.message.reply_text(output_message)
    else:
        update.message.reply_text("Start a connection first with /connect")


def disconnect(bot, update, user_data):
    """
    Disconnect from the current SSH connection and remove user variables
    """
    if 'client' in user_data:
        # Close SSH connection
        user_data['client'].close()

        # Remove all stored values from the user
        user_data.pop('client', None)
        user_data.pop('username', None)
        user_data.pop('password', None)
        user_data.pop('ip', None)
        user_data.pop('route', None)
        user_data.pop('computers', None)

    menu.main_menu(bot, update, user_data)


# ######################################################################
#                                MAIN
# ######################################################################
def main():
    # Parse arguments from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="JSON file with the Bot Configuration")
    args = parser.parse_args()

    # Open the config.json file
    if (args.config):
        helper.config = helper.open_json_file(args.config)
    else:
        helper.config = helper.open_json_file(helper.DEFAULT_CONFIG_FILEPATH)

    # Create folders and files from config.json structure if missing
    helper.create_folder_structure_from_config(
        'config/', helper.config['structure']['single'],
        helper.config['structure']['multiple'])

    # Check if token is defined in the config.json
    if 'token' not in helper.config:
        print("Missing 'token' field in the config.json! Please introduce " +
              "your token bot before starting")
        return

    # Create the EventHandler and pass it your bot's token.
    try:
        updater = Updater(helper.config['token'])
    except InvalidToken:
        print("Invalid Token! Please check your token in the config.json file")
        return

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, pass_user_data=True))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("run", run, pass_args=True))
    dp.add_handler(CommandHandler("wol", wake_on_lan_command, pass_args=True))
    dp.add_handler(
        CommandHandler(
            "send", send_command_to_client, pass_user_data=True,
            pass_args=True))
    dp.add_handler(
        CommandHandler(
            "sudo", run_as_root, pass_user_data=True, pass_args=True))
    dp.add_handler(
        CommandHandler("rrun", remote_run, pass_user_data=True, pass_args=True))

    # Add all conversation callbacks
    conversation.add_conversation_callbacks(dp)

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
