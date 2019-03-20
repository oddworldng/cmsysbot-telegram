from telegram import Bot
from telegram.ext import Updater

import helper

from view import view
from utils import computers_json, session
from states import State


def new_main(bot: Bot, update: Updater, user_data: dict):

    if not 'session' in user_data:
        user_data['session'] = session.Session()

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
        route, helper.config.get_sections(route),
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
        route, helper.config.get_sections(route),
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
    user_data['session'].computers = computers_json.Computers(filepath)

    user_data['session'].route = route

    # View
    view.ip_selection(
        route,
        user_data['session'].computers.get_computers(),
        return_to=State.CONNECT).edit(update)


def confirm_connect_ip(bot: Bot, update: Updater, user_data: dict):

    # Get the clicked ip
    user_data['session'].bridge_ip = update.callback_query.data

    # Text
    text = "Connect to %s?" % user_data['session'].bridge_ip

    # View
    view.yes_no(text, State.GET_CREDENTIALS, State.MAIN).edit(update)
