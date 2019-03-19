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


def confirm_connection_menu(bot: Bot, update: Updater, user_data: dict):
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

    # TRIGGERED if a Return to 'main_menu' button is clicked
    dp.add_handler(
        CallbackQueryHandler(
            main_menu, pattern=State.MAIN, pass_user_data=True))

    # TRIGGERED if clicked on 'Connect' from 'main_menu', or Return from
    # 'section_menu'
    dp.add_handler(
        CallbackQueryHandler(
            connect_menu, pattern=State.CONNECT, pass_user_data=True))

    # TRIGGERED if clicked on any department with multiple sections
    dp.add_handler(
        CallbackQueryHandler(
            structure_menu, pattern=with_subsections_regex,
            pass_user_data=True))

    # TRIGGERED if clicked on any department without sections (single)
    dp.add_handler(
        CallbackQueryHandler(
            ip_selection_menu,
            pattern=without_subsections_regex,
            pass_user_data=True))

    # TRIGGERED by an Ip (Even if its invalid)
    dp.add_handler(
        CallbackQueryHandler(
            get_ip, pattern="^[\d*\.*]*$", pass_user_data=True))

    # TRIGGERED if clicked on No in the 'confirm_connection_menu'
    dp.add_handler(
        CallbackQueryHandler(main_menu, pattern="^Ip-No$", pass_user_data=True))

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
