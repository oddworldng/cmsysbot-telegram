from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import CallbackQueryHandler

import helper
import ipaddress
import main
import computers_json


def new_menu(bot, update, user_data):
    """ENTRY POINT. Spawn a new menu in a new message"""
    message = helper.getMessage(update)
    message.reply_text(
        text=main_menu_message(user_data),
        reply_markup=main_menu_keyboard(user_data))


# ######################################################################
#                               MAIN MENU
# ######################################################################
def main_menu(bot, update, user_data):
    """Show the main menu, with the most basic options for the bot"""
    query = update.callback_query
    query.message.edit_text(
        text=main_menu_message(user_data),
        reply_markup=main_menu_keyboard(user_data))


def main_menu_message(user_data):
    """
    Message with the actual status of the bot (Connnected, Not connected, Host,
    User...)
    """
    message = "-- CmSysBot --\n"
    if 'client' in user_data:
        message += "CONNECTED:\n"
        if 'route' in user_data:
            message += "-> Localization: " + user_data['route'] + "\n"
        message += "-> Ip: " + user_data['ip'] + "\n"
        message += "-> USER: " + user_data['username'] + "\n"

    else:
        message += "NOT CONNECTED"

    message += "\nIssue your command."

    return message


def main_menu_keyboard(user_data):
    strings = []
    if 'client' in user_data:
        strings.extend([
            "Update Ips", "Filter computers", "Wake computers", "Shutdown",
            "Update computers", "Install software", "Execute script",
            "Upload file"
        ])
    else:
        strings.extend(["Connect", "Wake computers"])

    return build_keyboard(strings, n_cols=2)


# ######################################################################
#                          DEPARTMENT MENU
# ######################################################################
def department_menu(bot, update, user_data):
    """
    Show a menu with all the departments in the config.json
    """
    query = update.callback_query

    # Reset the temporal selected route (department/section)
    user_data.pop('temp_route', None)

    query.message.edit_text(
        text=department_menu_message(), reply_markup=department_menu_keyboard())


def department_menu_message():
    message = "DEPARTMENTS - Select your department:"
    return message


def department_menu_keyboard():
    """
    Keyboard with a button for each department name.
    Also, show an additional button for connecting to a specific Ip
    Also, show a Return button to go back to 'main menu'
    """
    # Names of all the departments (multiple and single)
    department_names = helper.get_department_names()

    return build_keyboard(
        department_names,
        n_cols=2,
        footer_buttons=[
            create_button("Connect to a specific Ip", "Ask-Ip"),
            create_button("Return", "Main")
        ])


# ######################################################################
#                            SECTION MENU
# ######################################################################
def section_menu(bot, update, user_data):
    """
    Show a menu with all the sections that a multiple department has
    """
    query = update.callback_query

    # Save the current selected department in the user_data
    user_data['temp_route'] = query.data

    query.message.edit_text(
        text=section_menu_message(user_data),
        reply_markup=section_menu_keyboard(user_data))


def section_menu_message(user_data):
    message = (
        "Current route: " + user_data['temp_route'] + "\nSelect your section: ")

    return message


def section_menu_keyboard(user_data):
    """
    Keyboard with a button for each section name for the selected department
    Also show a Return button to go back to 'department menu'
    """
    section_names = helper.get_section_names_for_department(
        user_data['temp_route'])

    # Create keyboard with a button for each section and a return button
    return build_keyboard(
        section_names,
        n_cols=2,
        footer_buttons=[create_button("Return", "Connect")])


# ######################################################################
#                           IP SELECTION MENU
# ######################################################################
def ip_selection_menu(bot, update, user_data):
    """
    Show a menu with the list of the computers that have a defined 'ip' field
    in the corresponding .json file
    """
    query = update.callback_query

    # Update the current route to add the section
    if 'temp_route' in user_data:  # department/section.json
        user_data['temp_route'] += '/' + query.data
    else:  # section.json
        user_data['temp_route'] = query.data

    # Create a path to the .json file from the temp_route
    filepath = 'config/' + user_data['temp_route'] + '.json'

    user_data['temp_computers'] = computers_json.Computers(filepath)

    query.message.edit_text(
        text=ip_selection_menu_message(user_data),
        reply_markup=ip_selection_menu_keyboard(user_data))


def ip_selection_menu_message(user_data):
    message = ("Current route: " + user_data['temp_route'] + "\n" +
               "Now,  Select a 'bridge' computer for the local connection. " +
               "All commands and scripts will be issued from this computer")

    return message


def ip_selection_menu_keyboard(user_data):
    """
    Keyboard with a button for each computer in the 'computers' array.
    Only add computers that have the 'ip' field defined
    Also show a Return button to go back to 'section menu'
    """
    # Get a list with the name and ip for each computers in the JSON,
    # BUT ONLY if the entry has an ip value assigned
    keyboard = []
    for computer in user_data['temp_computers'].get_computers():
        keyboard.append(
            InlineKeyboardButton(text=str(computer), callback_data=computer.ip))

    return InlineKeyboardMarkup(
        build_menu(
            keyboard, footer_buttons=[create_button("Return", "Connect")]))


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

        new_menu(bot, update, user_data)


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
        CallbackQueryHandler(main_menu, pattern="Main", pass_user_data=True))

    # TRIGGERED if clicked on 'Connect' from 'main_menu', or Return from
    # 'section_menu'
    dp.add_handler(
        CallbackQueryHandler(
            department_menu, pattern="Connect", pass_user_data=True))

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
