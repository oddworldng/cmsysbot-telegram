"""
In this module are defined all the ``general`` :obj:`callbacks` used by the
bot.

Note:
    A :obj:`callback` is any function that is called when pressing a button on
    a :obj:`Keyboard`. For example, when pressing on ``Connect``, ``Wake
    computers``, ``Disconnect``...

``general`` :obj:`callbacks` are the ones that perform any action, like
connecting, disconnecting, sending commands, sending messages, etc.

``general`` :obj:`callbacks` DON'T show/create new menus, only perform actions.
The callbacks used to move between menus must be defined inside the :obj:`menu`
module.
"""

import re

from telegram import Bot, Document, File
from telegram.ext import Updater

import view
from system import remote, bridge
from utils import State


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

    session: Session = user_data['session']

    # Get all the local ips for every mac
    local_ips = remote.get_local_ips(session.client, session.password,
                                     session.computers.get_macs())

    query = update.callback_query

    for computer in session.computers.get_included_computers():
        print(computer.mac)
        if computer.mac in local_ips:
            computer.ip = local_ips[computer.mac]

            query.message.reply_text("Computer %s with mac [%s] now has the \
ip %s" % (computer.name, computer.mac, computer.ip))


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
        remote.wake_on_lan(mac)

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
            remote.shutdown_computer(client, target_ip, username, password)

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
        remote.update_computer(client, target_ip, username, password)

        query.message.reply_text("Updated computer with ip %s" % target_ip)


def download_script(bot: Bot, update: Updater, user_data: dict):

    session = user_data['session']
    message = update.message

    if not session.connected:
        message.reply_text("You must be connected to a bridge computer before sending files!")
        return

    # Download the file
    file_object = message.document.get_file()
    download_path = "/tmp/%s" % message.document.file_name
    file_object.download(download_path)

    computers = user_data['session'].computers
    client = user_data['session'].client
    username = user_data['session'].username
    password = user_data['session'].password

    # Copiar al bridge
    bridge.send_file(client, download_path, "/tmp/")

    # Ejecutar desde el bridge
    for computer in computers.get_included_computers():
        message.reply_text("Sending script to computer %s" % computer.mac);

        target_ip = computer.ip


        # TODO: Send script
