from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import CallbackQueryHandler

import helper
import ipaddress
import main
import computers_json
import views

from states import State


def main_menu(bot, update, user_data):
    """Show the main menu, with the most basic options for the bot"""
    message = helper.getMessage(update)
    views.not_connected_view(message)


def connect_menu(bot, update, user_data):
    user_data['temp_route'] = []

    message = helper.getMessage(update)
    views.structure_view(
        message,
        "Select the department to connect:",
        [section.name for section in helper.config.get_sections()],
        return_to=State.MAIN)


def structure_menu(bot, update, user_data):
    next_section = update.callback_query.data

    if user_data['temp_route'] and user_data['temp_route'][-1] == next_section:
        user_data['temp_route'].pop()
    else:
        user_data['temp_route'].append(next_section)

    text = "Route: %s" % "/".join(user_data['temp_route'])

    return_to = ""
    if len(user_data['temp_route']) <= 1:
        return_to = State.CONNECT
    else:
        return_to = user_data['temp_route'][-1]

    message = helper.getMessage(update)
    views.structure_view(
        message,
        text, [
            section.name
            for section in helper.config.get_sections(user_data['temp_route'])
        ],
        return_to=return_to)


def ip_selection_menu(bot, update, user_data):
    """
    Show a menu with the list of the computers that have a defined 'ip' field
    in the corresponding .json file
    """
    section = update.callback_query.data
    user_data['temp_route'].append(section)

    # Create a path to the .json file from the temp_route
    filepath = "config/%s.json" % "/".join(user_data['temp_route'])
    user_data['temp_computers'] = computers_json.Computers(filepath)

    message = helper.getMessage(update)
    views.ip_selection_view(
        message,
        user_data['temp_computers'].get_computers(),
        return_to=State.CONNECT)


# ######################################################################
#                       CONFIRM CONNECTION MENU
# ######################################################################
def confirm_connection_menu(bot, update, user_data):
    """
    Check if the Ip is valid and show a "Yes/No" keyboard to the user.
    If the Ip is invalid, return to the 'main_menu'
    """
    try:
        ipaddress.ip_address(user_data['temp_ip'])
        if update.message:
            update.message.reply_text(
                text=confirm_connection_menu_message(user_data),
                reply_markup=confirm_connection_menu_keyboard())
        else:
            update.callback_query.message.edit_text(
                text=confirm_connection_menu_message(user_data),
                reply_markup=confirm_connection_menu_keyboard())

    except ValueError:
        text = user_data['temp_ip'] + " is not a valid ip!"
        if update.message:
            update.message.reply_text(text)
        else:
            update.callback_query.message.edit_text(text)

        # new_menu(bot, update, user_data)


def confirm_connection_menu_message(user_data):
    return ("Are you sure that you want to connect to: " +
            user_data['temp_ip'] + "?")


def confirm_connection_menu_keyboard():
    """Simple Yes or No promt"""
    keyboard = [
        InlineKeyboardButton("Yes", callback_data="Ip-Yes"),
        InlineKeyboardButton("No", callback_data="Ip-No")
    ]

    return InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))


def get_ip(bot, update, user_data):
    """Get user ip (from CallbackQueryHandler)"""
    query = update.callback_query
    user_data['temp_ip'] = query.data
    confirm_connection_menu(bot, update, user_data)


# ######################################################################
#                          HELPER FUNCTIONS
# ######################################################################
def build_keyboard(strings, n_cols=2, header_buttons=None, footer_buttons=None):
    """
    Return an InlineKeyboard with sane defaults. callback_data values will be
    the same value as the button labels
    """
    keyboard = [InlineKeyboardButton(s, callback_data=s) for s in strings if s]

    return InlineKeyboardMarkup(
        build_menu(keyboard, n_cols, header_buttons, footer_buttons))


def build_menu(buttons, n_cols=1, header_buttons=None, footer_buttons=None):
    """
    Build a menu from a list of InlineButtons (With multiple columns, extra
    buttons on top/botton...)
    """
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.extend(footer_buttons)

    return menu


def create_button(label, callback_data):
    """ Alias function for creating an InlineKeyboardButton """
    return [InlineKeyboardButton(label, callback_data=callback_data)]


# ######################################################################
#                              CALLBACKS
# ######################################################################
def add_menu_callbacks(dp):
    """Add all the callback handlers to the Dispatcher"""
    sections = [
        "^%s$" % section.name
        for section in helper.config.get_sections_with_subsections()
    ]

    nosections = [
        "^%s$" % section.name
        for section in helper.config.get_sections_without_subsections()
    ]

    sections_regex = "|".join(sections)
    nosections_regex = "|".join(nosections)

    print(sections_regex)
    print(nosections_regex)

    # TRIGGERED if a Return to 'main_menu' button is clicked
    dp.add_handler(
        CallbackQueryHandler(
            main_menu, pattern=State.MAIN, pass_user_data=True))

    # TRIGGERED if clicked on 'Connect' from 'main_menu', or Return from
    # 'section_menu'
    dp.add_handler(
        CallbackQueryHandler(
            connect_menu, pattern=State.CONNECT, pass_user_data=True))

    # TRIGGERED if clicked on Disconnect after connecting
    dp.add_handler(
        CallbackQueryHandler(
            main.disconnect, pattern="Disconnect", pass_user_data=True))

    # TRIGGERED if clicked on any department with multiple sections
    dp.add_handler(
        CallbackQueryHandler(
            structure_menu, pattern=sections_regex, pass_user_data=True))

    # TRIGGERED if clicked on any department without sections (single)
    dp.add_handler(
        CallbackQueryHandler(
            ip_selection_menu, pattern=nosections_regex, pass_user_data=True))

    # TRIGGERED if clicked on any section from the 'section_names' array
    dp.add_handler(
        CallbackQueryHandler(
            ip_selection_menu, pattern=sections_regex, pass_user_data=True))

    # TRIGGERED by an Ip (Even if its invalid)
    dp.add_handler(
        CallbackQueryHandler(
            get_ip, pattern="^[\d*\.*]*$", pass_user_data=True))

    # TRIGGERED if clicked on No in the 'confirm_connection_menu'
    dp.add_handler(
        CallbackQueryHandler(main_menu, pattern="^Ip-No$", pass_user_data=True))

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
