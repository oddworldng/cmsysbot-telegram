from telegram import Bot
from telegram.ext import Updater

import view
from utils import Computers, State, glob


def new_main(bot: Bot, update: Updater, user_data: dict):

    s = user_data['session']

    # View
    if not s.connected:
        view.not_connected().reply(update)
    else:
        view.connected(s.route, s.username, s.bridge_ip).reply(update)


def main(bot: Bot, update: Updater, user_data: dict):
    """Show the main menu, with the most basic options for the bot"""

    s = user_data['session']

    # View
    if not s.connected:
        view.not_connected().edit(update)
    else:
        view.connected(s.route, s.username, s.bridge_ip).edit(update)


def select_department(bot: Bot, update: Updater, user_data: dict):

    # TODO: Document route
    user_data['session'].route = []  # Reset route
    route = user_data['session'].route

    print(route)

    # View
    view.structure(
        route, glob.config_file.get_sections(route),
        return_to=State.MAIN).edit(update)


def structure(bot: Bot, update: Updater, user_data: dict):

    # Get the clicked section
    next_section = update.callback_query.data

    route = user_data['session'].route
    print(route)

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
    user_data['session'].route = route
    print(user_data['session'].route)

    # View
    view.structure(
        route, glob.config_file.get_sections(route),
        return_to=return_to).edit(update)


def ip_selection(bot: Bot, update: Updater, user_data: dict):
    """
    Show a menu with the list of the computers that have a defined 'ip' field
    in the corresponding .json file
    """

    route = user_data['session'].route

    # Get the clicked section
    next_section = update.callback_query.data
    route.append(next_section)

    # Create a path to the .json file from the route
    filepath = "config/%s.json" % "/".join(route)
    user_data['session'].computers = Computers(filepath)

    user_data['session'].route = route

    # View
    view.ip_selection(
        route,
        user_data['session'].computers.get_computers(),
        return_to=State.CONNECT).edit(update)


def confirm_connect_ip(bot: Bot, update: Updater, user_data: dict):

    # Get the clicked ip
    user_data['session'].bridge_ip = update.callback_query.data

    # View
    text = "Connect to %s?" % user_data['session'].bridge_ip
    view.yes_no(
        text,
        yes_callback_data=State.GET_CREDENTIALS,
        no_callback_data=State.MAIN).edit(update)


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

    session = user_data['session']

    # Try to connect to the client
    session.start_connection()

    text = ""
    if session.connected:
        text = "Successfully connected to %s!" % session.bridge_ip
    else:
        text = "Unable to connect to %s.\n\
Please try to login with different credentials!" % session.bridge_ip

    # Send the status message
    update.message.reply_text(text)

    # Show the main menu again
    new_main(bot, update, user_data)


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
    new_main(bot, update, user_data)


def filter_computers(bot: Bot, update: Updater, user_data: dict):
    # View
    computers = user_data['session'].computers

    view.filter_computers(computers).edit(update)
