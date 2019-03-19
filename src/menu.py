from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler

import helper
import ipaddress
import main
from utils import computers_json
import views

from states import State


def new_main(bot: Bot, update: Updater, user_data: dict):
    # View
    views.not_connected_view().reply(update)


def main(bot: Bot, update: Updater, user_data: dict):
    """Show the main menu, with the most basic options for the bot"""
    # View
    views.not_connected_view().edit(update)


def connect(bot: Bot, update: Updater, user_data: dict):
    user_data['temp_route'] = []

    # View
    views.structure_view(
        user_data['temp_route'],
        helper.config.get_sections(user_data['temp_route']),
        return_to=State.MAIN).edit(update)


def structure(bot: Bot, update: Updater, user_data: dict):
    # Get the clicked section
    next_section = update.callback_query.data

    # Remove section from the route if going backwards, otherwise append
    if user_data['temp_route'] and user_data['temp_route'][-1] == next_section:
        user_data['temp_route'].pop()
    else:
        user_data['temp_route'].append(next_section)

    # Return to the last section, or to the Connect menu if its the start oits
    # the start of the route
    return_to = ""
    if len(user_data['temp_route']) <= 1:
        return_to = State.CONNECT
    else:
        return_to = user_data['temp_route'][-1]

    # View
    views.structure_view(
        user_data['temp_route'],
        helper.config.get_sections(user_data['temp_route']),
        return_to=return_to).edit(update)


def ip_selection(bot: Bot, update: Updater, user_data: dict):
    """
    Show a menu with the list of the computers that have a defined 'ip' field
    in the corresponding .json file
    """
    # Get the clicked section
    next_section = update.callback_query.data
    user_data['temp_route'].append(next_section)

    # Create a path to the .json file from the temp_route
    filepath = "config/%s.json" % "/".join(user_data['temp_route'])
    user_data['temp_computers'] = computers_json.Computers(filepath)

    # View
    views.ip_selection_view(
        user_data['temp_route'],
        user_data['temp_computers'].get_computers(),
        return_to=State.CONNECT).edit(update)


def confirm_connect_ip(bot: Bot, update: Updater, user_data: dict):
    # Get the clicked ip
    selected_ip = update.callback_query.data
    user_data['temp_ip'] = selected_ip

    # Text
    text = "Connect to %s?" % selected_ip

    # View
    views.yes_no_view(text, State.GET_CREDENTIALS, State.MAIN).edit(update)
