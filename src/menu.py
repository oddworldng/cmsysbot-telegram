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


def department_menu(bot, update, user_data):
    """
    Show a menu with all the departments in the config.json
    """
    # Reset the temporal selected route (department/section)
    user_data['temp_route'] = []
    print(user_data['temp_route'])

    message = helper.getMessage(update)
    views.structure_view(
        message,
        "Select your department",
        helper.get_department_names(),
        return_to=State.MAIN)


def section_menu(bot, update, user_data):
    # Save the current selected department in the user_data
    department = update.callback_query.data

    if not user_data['temp_route']:
        user_data['temp_route'].append(department)

    if department is not user_data['temp_route'][-1]:
        user_data['temp_route'].pop()

    print(user_data['temp_route'])

    message = helper.getMessage(update)
    views.structure_view(
        message,
        "Select your section",
        helper.get_section_names_for_department(department),
        return_to=State.DEPARTMENTS)


# ######################################################################
#                           IP SELECTION MENU
# ######################################################################
def ip_selection_menu(bot, update, user_data):
    """
    Show a menu with the list of the computers that have a defined 'ip' field
    in the corresponding .json file
    """
    return_to = ""
    if not user_data['temp_route']:
        return_to = State.DEPARTMENTS
    else:
        return_to = user_data['temp_route'][-1]

    section = update.callback_query.data
    user_data['temp_route'].append(section)

    print(user_data['temp_route'])

    # Create a path to the .json file from the temp_route
    filepath = 'config/' + '/'.join(user_data['temp_route']) + '.json'
    user_data['temp_computers'] = computers_json.Computers(filepath)

    message = helper.getMessage(update)
    views.ip_selection_view(
        message,
        user_data['temp_computers'].get_computers(),
        return_to=return_to)


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
    multiples = helper.get_multiple_department_names()
    singles = helper.get_single_department_names()
    sections = []
    for department in multiples:
        sections.extend(helper.get_section_names_for_department(department))

    # Construct a simple regex that match every name
    departments_regex = "|".join(multiples)
    sections_regex = "|".join(sections)
    singles_regex = "|".join(singles)

    # TRIGGERED if a Return to 'main_menu' button is clicked
    dp.add_handler(
        CallbackQueryHandler(
            main_menu, pattern=State.MAIN, pass_user_data=True))

    # TRIGGERED if clicked on 'Connect' from 'main_menu', or Return from
    # 'section_menu'
    dp.add_handler(
        CallbackQueryHandler(
            department_menu, pattern=State.DEPARTMENTS, pass_user_data=True))

    # TRIGGERED if clicked on Disconnect after connecting
    dp.add_handler(
        CallbackQueryHandler(
            main.disconnect, pattern="Disconnect", pass_user_data=True))

    # TRIGGERED if clicked on any department with multiple sections
    dp.add_handler(
        CallbackQueryHandler(
            section_menu, pattern=departments_regex, pass_user_data=True))

    # TRIGGERED if clicked on any department without sections (single)
    dp.add_handler(
        CallbackQueryHandler(
            ip_selection_menu, pattern=singles_regex, pass_user_data=True))

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
