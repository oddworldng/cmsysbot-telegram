from telegram import Bot
from telegram.ext import Updater

import paramiko

import re

from controller import menu
from cmsys import action
from states import State
from view import view
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


def update_ips(bot: Bot, update: Updater, user_data: dict):

    client = user_data['session'].client
    macs = user_data['session'].computers.get_macs()
    password = user_data['session'].password

    result_macs, result_ips = action.get_associated_ips(client, password, macs)

    print(result_macs)
    print(result_ips)t 



def include_computers(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    # Get target ( 'all' or a computer mac)
    target = re.search(State.INCLUDE_COMPUTERS, query.data).group(1)

    computers = user_data['session'].computers

    if target == 'all':
        for computer in computers.get_computers():
            computer.included = True
    else:
        computers.find(target).included = True

    # Redraw view
    view.filter_computers(computers).edit(update)


def exclude_computers(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    # Get target ( 'all' or a computer mac)
    target = re.search(State.EXCLUDE_COMPUTERS, query.data).group(1)

    computers = user_data['session'].computers

    if target == 'all':
        for computer in computers.get_computers():
            computer.included = False
    else:
        computers.find(target).included = False

    # Redraw view
    view.filter_computers(computers).edit(update)


def wake_computers(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    computers = user_data['session'].computers

    for computer in computers.get_included_computers():
        mac = computer.mac

        action.wake_on_lan(mac)
        query.message.reply_text("Waking up computer with mac %s..." % mac)


# TODO: ¿Maybe ask if turn down bridge computer too?
def shutdown_computers(bot: Bot, update: Updater, user_data: dict):
    query = update.callback_query

    client = user_data['session'].client
    computers = user_data['session'].computers
    bridge_ip = user_data['session'].bridge_ip
    username = user_data['session'].username
    password = user_data['session'].password

    for computer in computers.get_included_computers():
        target_ip = computer.ip

        if target_ip != bridge_ip:  # Don't shutdown bridge ip
            action.shutdown_computer(client, target_ip, username, password)
