import re

import paramiko
from telegram import Bot
from telegram.ext import Updater

import view
from cmsys import action
from utils import State

from . import menu


def connect(bot: Bot, update: Updater, user_data: dict):
    """
    Tries to open a SSH connection from the bot server to the bridge computer.

    After that, sends a message to the chat with the result of the connection
    (successed or failed) and returns to the main menu.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    try:
        session = user_data['session']

        # Try to connect to the client
        session.start_connection()

        # Return a successful connection message
        update.message.reply_text(
            "Successfully connected to %s!\n" % session.bridge_ip)

    except paramiko.AuthenticationException as error:
        # Return a failed connection message
        update.message.reply_text(
            str(error) + " Please try to login with different credentials!")

    finally:
        # Show the main menu again
        menu.new_main(bot, update, user_data)


def disconnect(bot: Bot, update: Updater, user_data: dict):
    """
    Closes the open SSH connection to the bridge computer.

    After that, sends a 'Disconnected' message to the chat and returns to the
    main menu.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    # Close the connection
    user_data['session'].end_connetion()

    message = update.callback_query.message
    message.edit_text("Disconnect...")

    # Show the main menu again
    menu.new_main(bot, update, user_data)


def update_ips(bot: Bot, update: Updater, user_data: dict):
    """
    Get all the macs and its associated ips from the local network. Then,
    iterate through all the computers in :obj:`Computers`. If one of the
    computer macs match with one of the local macs, update its associated ip to
    the new value.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """
    # TODO: WIP. Iterate through the computer macs and change the ips

    client = user_data['session'].client
    macs = user_data['session'].computers.get_macs()
    password = user_data['session'].password

    # Get all the local macs and ips
    result_macs, result_ips = action.get_associated_ips(client, password, macs)

    print(result_macs)
    print(result_ips)


def include_computers(bot: Bot, update: Updater, user_data: dict):
    """
    Change the attribute :obj:`included` for one/all computers to ``True``. If
    a computer is included, it will be yielded in the loop while using the
    :obj:`Computers.get_included_computers()` function.

    Note:
        The :obj:`query.data` value used by this function will be either the
        string ``include-all`` for all computers, or ``include-[mac_address]``
        for one computer.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    query = update.callback_query

    # Extract the target from the string. Values: 'all' or '[mac_address]'
    target = re.search(State.INCLUDE_COMPUTERS, query.data).group(1)

    computers = user_data['session'].computers

    # Include all computers
    if target == 'all':
        for computer in computers.get_computers():
            computer.included = True

    # Find the computer with the specified mac and include it
    else:
        computers.find(target).included = True

    # Redraw the view
    view.filter_computers(computers).edit(update)


def exclude_computers(bot: Bot, update: Updater, user_data: dict):
    """
    Change the attribute :obj:`included` for one/all computers to ``False``. If
    a computer is not included, it won't be yielded in the loop while using the
    :obj:`Computers.get_included_computers()` function.

    Note:
        The :obj:`query.data` value used by this function will be either the
        string ``exclude-all`` for all computers, or ``exclude-[mac_address]``
        for one computer.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    query = update.callback_query

    # Extract the target from the string. Values: 'all' or '[mac_address]'
    target = re.search(State.EXCLUDE_COMPUTERS, query.data).group(1)

    computers = user_data['session'].computers

    # Exclude all computers
    if target == 'all':
        for computer in computers.get_computers():
            computer.included = False

    # Find the computer with the specified mac and exclude it
    else:
        computers.find(target).included = False

    # Redraw the view
    view.filter_computers(computers).edit(update)


def wake_computers(bot: Bot, update: Updater, user_data: dict):
    """
    Iterate through the ``included`` computers and send a wake-on-lan command.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    query = update.callback_query

    computers = user_data['session'].computers

    # Iterate only through the included computers
    for computer in computers.get_included_computers():
        mac = computer.mac

        # Send the wake-on-lan command
        action.wake_on_lan(mac)

        query.message.reply_text("Waking up computer with mac %s..." % mac)


def shutdown_computers(bot: Bot, update: Updater, user_data: dict):
    """
    Iterate through the ``included`` computers and send a shutdown command.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    # TODO: ¿Maybe ask if turn down bridge computer too?

    query = update.callback_query

    # Get all necessary data for sending the command
    client = user_data['session'].client
    computers = user_data['session'].computers
    bridge_ip = user_data['session'].bridge_ip
    username = user_data['session'].username
    password = user_data['session'].password

    # Iterate only through the included computers
    for computer in computers.get_included_computers():
        target_ip = computer.ip

        if target_ip != bridge_ip:  # Don't shutdown bridge computer
            # Send the shutdown command
            action.shutdown_computer(client, target_ip, username, password)

            query.message.reply_text(
                "Shutdown computer with ip %s" % target_ip)


def update_computers(bot: Bot, update: Updater, user_data: dict):
    """
    Iterate through the ``included`` computers and send an update command.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    # TODO: Improve the returned message. Tell if the computer is already
    # updated, or the number of packages to update.

    query = update.callback_query

    # Get all necessary data for sending the command
    client = user_data['session'].client
    computers = user_data['session'].computers
    username = user_data['session'].username
    password = user_data['session'].password

    # Iterate only through the included computers
    for computer in computers.get_included_computers():
        target_ip = computer.ip

        # Send the update command
        action.update_computer(client, target_ip, username, password)

        query.message.reply_text("Updated computer with ip %s" % target_ip)
