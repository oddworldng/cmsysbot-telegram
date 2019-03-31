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
from system import bridge
from utils import State, plugins


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
    session = user_data['session']

    # Get all the local ips for every local mac
    local_ips = bridge.get_local_ips(session)

    message = update.callback_query.message

    for computer in session.computers.get_included_computers():
        if computer.mac in local_ips:
            last_ip = computer.ip

            computer.ip = local_ips[computer.mac]

            message.reply_text("Computer %s: %s --> %s" %
                               (computer.name, last_ip, computer.ip))


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
