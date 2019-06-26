"""
In this module are defined all the ``general`` :obj:`callbacks` used by the
bot.

Note:
    A :obj:`callback` is any function that is called when pressing a button on
    a :obj:`Keyboard`. For example, when pressing on ``Connect``, ``Wake
    computers``, ``Disconnect``...

``general`` :obj:`callbacks` are the ones that perform any action, like
connecting, disconnecting, sending commands, sending messages, etc.
"""

import re

from telegram import Bot
from telegram.ext import Job, JobQueue, Updater

from cmsysbot import view
from cmsysbot.system import Plugin
from cmsysbot.utils import Session, State, states
from cmsysbot.utils.decorators import connected, not_connected

from . import menu


@not_connected
def connect(bot: Bot, update: Updater, user_data: dict, job_queue: JobQueue):
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

    session = Session.get_from(user_data)

    # Try to connect to the client
    session.start_connection()

    # Send the status message
    view.connect_output(session).reply(update)

    if session.connected:
        # Check if the bridge computer has all the required dependencies
        initialize_bridge(bot, update, user_data)

        # Check the status of each computers (which are alive or unreachable)
        update_computers_status(user_data)

        job_queue.run_repeating(
            job_update_computers_status,
            interval=states.config_file.check_status_interval,
            context=user_data,
        )

    # Show the main menu again
    menu.new_main(bot, update, user_data)


@connected
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

    bridge_ip = Session.get_from(user_data).bridge_ip

    # Save the new status of the computers
    Session.get_from(user_data).computers.save()

    # Close the connection
    Session.get_from(user_data).end_connetion()

    # Send the disconnect output
    view.disconnect_output(bridge_ip).edit(update)

    # Show the main menu again
    menu.new_main(bot, update, user_data)


@connected
def initialize_bridge(bot: Bot, update: Updater, user_data: dict):

    session = Session.get_from(user_data)

    plugin = Plugin("plugins/_bridge_initialization")

    name, ip, stdout, stderr = next(plugin.run(session))
    view.plugin_output(
        name, ip, "Bridge Initialization", stdout, stderr, hide_header=True
    ).reply(update)


def job_update_computers_status(bot: Bot, job: Job):
    user_data = job.context

    if Session.get_from(user_data).connected:
        update_computers_status(user_data)
    else:
        job.schedule_removal()


def update_computers_status(user_data: dict):

    session = Session.get_from(user_data)

    plugin = Plugin("plugins/_computers_status")
    _, _, stdout, _ = next(plugin.run(session))
    # The stdout has the format `{ip} is {status}`

    # TODO: Remove n^2 loop by adding dicts to the computers_json structure
    for line in stdout.splitlines():
        ip, _, status = line.split()

        for computer in session.computers:
            if ip == computer.ip:
                computer.status = status


@connected
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
    session = Session.get_from(user_data)

    # Get all the local ips for every local mac
    plugin = Plugin("plugins/_local_arp_scan")

    # Change view to executing
    view.plugin_start(plugin.name).edit(update)

    _, _, stdout, _ = next(plugin.run(session))

    local_ips = {}
    for line in stdout.splitlines():
        ip, mac = line.strip().split()
        local_ips[mac] = ip

    for computer in session.computers.get_included_computers():
        if computer.mac.lower() in local_ips:
            last_ip = computer.ip
            computer.ip = local_ips[computer.mac.lower()]

            view.update_ip_output(computer, last_ip).reply(update)

    session.computers.save()

    menu.new_main(bot, update, user_data)


@connected
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

    computers = Session.get_from(user_data).computers

    # Include all computers
    if target == "all":
        for computer in computers.get_computers():
            computer.included = True

    # Find the computer with the specified mac and include it
    else:
        computers.find(target).included = True

    # Redraw the view
    view.filter_computers(computers).edit(update)


@connected
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

    computers = Session.get_from(user_data).computers

    # Exclude all computers
    if target == "all":
        for computer in computers.get_computers():
            computer.included = False

    # Find the computer with the specified mac and exclude it
    else:
        computers.find(target).included = False

    # Redraw the view
    view.filter_computers(computers).edit(update)
