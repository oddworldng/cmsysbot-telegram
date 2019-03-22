from telegram import Bot
from telegram.ext import Updater

import paramiko

from controller import menu
from cmsys import action
import helper


def connect(bot: Bot, update: Updater, user_data: dict):
    """
    Establish a SSH connection from the bot machine to the bridge computer
    """

    try:
        session = user_data['session']

        # Try to connect to the client
        session.start_connection()

        # Return a successful connection message
        update.message.reply_text(
            "Successfully connected to %s!\n" % session.bridge_ip)

    except paramiko.AuthenticationException as error:
        update.message.reply_text(
            str(error) + " Please try to login with different credentials!")

    finally:
        menu.new_main(bot, update, user_data)


def disconnect(bot: Bot, update: Updater, user_data: dict):
    user_data['session'].end_connetion()

    message = helper.getMessage(update)
    message.edit_text("Disconnect...")

    menu.new_main(bot, update, user_data)


# TODO: Filter computers
def wake_computers(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    computers = user_data['session'].computers

    for mac in computers.get_macs():
        action.wake_on_lan(mac)
        query.message.reply_text("Waking up computer with mac %s..." % mac)


# TODO: Filter computers (¿Maybe ask if turn down own computer?)
def shutdown_computers(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    client = user_data['session'].client
    computers = user_data['session'].computers
    bridge_ip = user_data['session'].bridge_ip
    username = user_data['session'].username
    password = user_data['session'].password

    for target_ip in computers.get_ips():
        if target_ip != bridge_ip:  # Don't shutdown bridge ip
            action.shutdown_computer(client, target_ip, username, password)


def include_computers(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    print(query.data)


def exclude_computers(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    print(query.data)
