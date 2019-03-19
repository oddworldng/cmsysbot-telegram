from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler

import helper
import ipaddress
import main
import computers_json
import views

from states import State


def new_menu(bot: Bot, update: Updater, user_data: dict):
    message = helper.getMessage(update)
    views.not_connected_view().reply(update)


def main_menu(bot: Bot, update: Updater, user_data: dict):
    """Show the main menu, with the most basic options for the bot"""
    views.not_connected_view().edit(update)


def connect_menu(bot: Bot, update: Updater, user_data: dict):
    user_data['temp_route'] = []

    views.structure_view(
        user_data['temp_route'],
        helper.config.get_sections(user_data['temp_route']),
        return_to=State.MAIN).edit(update)


def structure_menu(bot: Bot, update: Updater, user_data: dict):
    next_section = update.callback_query.data

    if user_data['temp_route'] and user_data['temp_route'][-1] == next_section:
        user_data['temp_route'].pop()
    else:
        user_data['temp_route'].append(next_section)

    return_to = ""
    if len(user_data['temp_route']) <= 1:
        return_to = State.CONNECT
    else:
        return_to = user_data['temp_route'][-1]

    views.structure_view(
        user_data['temp_route'],
        helper.config.get_sections(user_data['temp_route']),
        return_to=return_to).edit(update)


def ip_selection_menu(bot: Bot, update: Updater, user_data: dict):
    """
    Show a menu with the list of the computers that have a defined 'ip' field
    in the corresponding .json file
    """
    next_section = update.callback_query.data
    user_data['temp_route'].append(next_section)

    # Create a path to the .json file from the temp_route
    filepath = "config/%s.json" % "/".join(user_data['temp_route'])
    user_data['temp_computers'] = computers_json.Computers(filepath)

    views.ip_selection_view(
        user_data['temp_route'],
        user_data['temp_computers'].get_computers(),
        return_to=State.CONNECT).edit(update)


def confirm_connect_ip_menu(bot: Bot, update: Updater, user_data: dict):
    selected_ip = update.callback_query.data
    user_data['temp_ip'] = selected_ip

    text = "Do you want to connect to %s" % selected_ip

    views.yes_no_menu(text, State.GET_CREDENTIALS, State.MAIN).edit(update)


# ######################################################################
#                              CALLBACKS
# ######################################################################
def add_menu_callbacks(dp):
    """Add all the callback handlers to the Dispatcher"""

    with_subsections = []
    without_subsections = []

    for section in helper.config.get_all_sections():
        if section.has_subsections():
            with_subsections.append("^%s$" % section.name)
        else:
            without_subsections.append("^%s$" % section.name)

    with_subsections_regex = "|".join(with_subsections)
    without_subsections_regex = "|".join(without_subsections)

    print(with_subsections_regex)
    print(without_subsections_regex)

    # Show Main Menu
    dp.add_handler(
        CallbackQueryHandler(
            main_menu, pattern=State.MAIN, pass_user_data=True))

    # Show Connect Menu
    dp.add_handler(
        CallbackQueryHandler(
            connect_menu, pattern=State.CONNECT, pass_user_data=True))

    # Show structure of department (and subdepartments)
    dp.add_handler(
        CallbackQueryHandler(
            structure_menu, pattern=with_subsections_regex,
            pass_user_data=True))

    # When clicked in a section without subsections, show ip list
    dp.add_handler(
        CallbackQueryHandler(
            ip_selection_menu,
            pattern=without_subsections_regex,
            pass_user_data=True))

    # When clicked on an ip, show the menu asking if continuing the the
    # connection
    dp.add_handler(
        CallbackQueryHandler(
            confirm_connect_ip_menu,
            pattern=State.CONFIRM_CONNECT,
            pass_user_data=True))

    # TRIGGERED if clicked on Disconnect after connecting
    dp.add_handler(
        CallbackQueryHandler(
            main.disconnect, pattern="Disconnect", pass_user_data=True))

    # TRIGGERED if clicked on 'Wake Computers from the main menu'
    dp.add_handler(
        CallbackQueryHandler(
            main.wake_on_lan_callback,
            pattern="^Wake computers$",
            pass_user_data=True))

    # TRIGGERED if clicked on 'Shutdown computers from the main menu'
    dp.add_handler(
        CallbackQueryHandler(
            main.shutdown_computers_callback,
            pattern="^Shutdown$",
            pass_user_data=True))

    # TRIGGERED if clicked on 'Update Ips' from the main menu
    dp.add_handler(
        CallbackQueryHandler(
            main.update_ips, pattern="^Update Ips$", pass_user_data=True))
