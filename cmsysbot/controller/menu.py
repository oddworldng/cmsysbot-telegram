"""
In this module are defined all the ``menu`` :obj:`callbacks` used by the
bot.

Note:
    A :obj:`callback` is any function that is called when pressing a button on
    a :obj:`Keyboard`. For example, when pressing on ``Connect``, ``Wake
    computers``, ``Disconnect``...

``menu`` :obj:`callbacks` are the ones that handle the movement between
different menus (For example, from `main menu` to `select a department`)

``menu`` :obj:`callbacks` DON'T perform any other action other than handling
the movement, and some side effects like updating :obj:`user_data` variable or
sending some messages.

Callbacks that perform an action (like waking or shutting down computers,
updating computers/ips...) must be defined inside the :obj:`general` module.
"""

from telegram import Bot
from telegram.ext import Updater

from cmsysbot import view
from cmsysbot.system import Plugin
from cmsysbot.utils import Computers, State, states


def new_main(bot: Bot, update: Updater, user_data: dict):
    """
    Send a new message with a new main menu. Depending on if the user is
    connected or disconnected the view may change.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    session = user_data["session"]

    # View
    if not session.connected:
        view.not_connected().reply(update)
    else:
        view.connected(
            session.route,
            Plugin.get_local_plugins(),
            session.username,
            session.bridge_ip,
        ).reply(update)


def main(bot: Bot, update: Updater, user_data: dict):
    """
    Edit the last message to show the main menu. Depending on if the user is
    connected or disconnected the view may change.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    session = user_data["session"]

    # View
    if not session.connected:
        view.not_connected().edit(update)
    else:
        view.connected(
            session.route,
            Plugin.get_local_plugins(),
            session.username,
            session.bridge_ip,
        ).edit(update)


def select_department(bot: Bot, update: Updater, user_data: dict):
    """
    Show the nodes on the first level of the :obj:`structure` field on the
    :obj:`config.json` file.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    user_data["session"].route = []  # Reset route
    route = user_data["session"].route

    # View
    view.structure(
        route, states.config_file.get_sections(route), return_to=State.MAIN
    ).edit(update)


def structure(bot: Bot, update: Updater, user_data: dict):
    """
    Show the nodes on the level indicated by the route from the
    :obj:`config.json` file.

    Note:
        The buttons shown by this function change dynamically depending on the
        value of ``route``.

        For example, if we have the following :obj:`config.json` file:

        .. code-block:: python

            {
                "structure": [{
                    "name": "ESIT",
                    "sections": ["Industrial", "Ingeniería"]
                },
                {
                    "name": "MATFIS"
                }]
            }

        Calling this function with :obj:`remote = []` will show the buttons
        ``ESIT`` and ``MATFIS``, but calling this function with :obj:`remote =
        ['ESIT']` will show the buttons ``Industrial`` and ``Ingeniería``, and
        calling this function with :obj:`remote = ['MATFIS']` will show no
        buttons.

    Args:
        bot (:obj:`telegram.bot.Bot`): The telegram bot instance.
        update (:obj:`telegram.ext.update.Updater`): The Updater associated to
            the bot.
        user_data (:obj:`dict`): The dictionary with user variables.
    """

    # Get the clicked section
    next_section = update.callback_query.data

    route = user_data["session"].route

    # Remove section from the route if going backwards, otherwise append
    if route and route[-1] == next_section:
        route.pop()
    else:
        route.append(next_section)

    # Return to the last section, or to the Connect menu if its the start oits
    # the start of the route
    return_to = ""
    if len(route) <= 1:
        return_to = State.CONNECT
    else:
        return_to = route[-1]

    # Update the route
    user_data["session"].route = route

    # View
    view.structure(
        route, states.config_file.get_sections(route), return_to=return_to
    ).edit(update)


def ip_selection(bot: Bot, update: Updater, user_data: dict):
    """
    Show a menu with the list of the computers that have a defined 'ip' field
    in the corresponding .json file
    """

    route = user_data["session"].route

    # Get the clicked section
    next_section = update.callback_query.data
    route.append(next_section)

    # Create a path to the .json file from the route
    filepath = "config/%s.json" % "/".join(route)
    user_data["session"].computers = Computers(filepath)

    user_data["session"].route = route

    # View
    view.ip_selection(
        route, user_data["session"].computers.get_computers(), return_to=State.CONNECT
    ).edit(update)


def confirm_connect_ip(bot: Bot, update: Updater, user_data: dict):

    # Get the clicked ip
    user_data["session"].bridge_ip = update.callback_query.data

    # View
    text = "Connect to %s?" % user_data["session"].bridge_ip
    view.yes_no(
        text, yes_callback_data=State.GET_CREDENTIALS, no_callback_data=State.MAIN
    ).edit(update)


def filter_computers(bot: Bot, update: Updater, user_data: dict):

    # View
    computers = user_data["session"].computers
    view.filter_computers(computers).edit(update)
