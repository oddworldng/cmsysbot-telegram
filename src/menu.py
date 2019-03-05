from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import CallbackQueryHandler

import helper
import main


def new_menu(bot, update):
    """ENTRY POINT. Spawn a new menu in a new message"""
    message = helper.getMessage(update)
    message.reply_text(
        text=main_menu_message(), reply_markup=main_menu_keyboard())


# ##### MAIN MENU
def main_menu_message():
    return "Welcome to CmSysBot. Issue your command:"


def main_menu_keyboard():
    strings = ["Login", "Connect"]
    return build_keyboard(strings, n_cols=2)


def main_menu(bot, update):
    """Show the main menu, with the most basic options for the bot"""
    query = update.callback_query
    query.message.edit_text(
        text=main_menu_message(), reply_markup=main_menu_keyboard())


# ##### CONNECT MENU
def department_menu_message():
    return "DEPARTMENTS - Select your department:"


def department_menu_keyboard():
    """
    Keyboard with a button for each department in the 'structures' array.
    Also, show a button for connecting to a specific Ip
    Also, show a Return button to go back to 'main menu'
    """
    # Iterate through the JSON 'multiple' array and get all the names
    department_names = [o['name']
                        for o in helper.config['structure']['multiple']]
    # Also show the names of the 'singles'
    department_names.extend(helper.config['structure']['single'])

    return build_keyboard(
        department_names,
        n_cols=2,
        footer_buttons=[
            create_button("Connect to a specific Ip", "Ip"),
            create_button("Return", "Main")
        ])


def department_menu(bot, update, user_data):
    query = update.callback_query

    # Reset the last selected department
    user_data.pop('department', None)

    query.message.edit_text(
        text=department_menu_message(),
        reply_markup=department_menu_keyboard())


# ##### SECTION MENU
def section_menu_message(user_data):
    return ("Current department: " + user_data['department'] +
            "\nSelect your section: ")


def section_menu_keyboard(user_data):
    """
    Keyboard with a button for each section in the 'sections' array of
    department.
    Also show a Return button to go back to 'department menu'
    """
    # First, find the index of the selected department
    department_names = [o['name']
                        for o in helper.config['structure']['multiple']]
    index = department_names.index(user_data['department'])

    # Then, get an array with the names of all the sections in the department
    section_names = helper.config['structure']['multiple'][index]['sections']

    # Create keyboard with a button for each section and a return button
    return build_keyboard(
        section_names,
        n_cols=2,
        footer_buttons=[create_button("Return", "Connect")])


def section_menu(bot, update, user_data):
    query = update.callback_query

    # Save the current selected department in the user_data
    user_data['department'] = query.data

    query.message.edit_text(
        text=section_menu_message(user_data),
        reply_markup=section_menu_keyboard(user_data))


# ##### IP MENU
def ip_selection_menu_message(user_data):
    output = ""
    if 'department' in user_data:
        output += "Current department: " + user_data['department'] + "\n"

    if 'section' in user_data:
        output += "Current section: " + user_data['section'] + "\n"

    output += ("Now,  Select a 'bridge' computer for the local connection. " +
               "All commands and scripts will be issued from this computer")

    return output


def ip_selection_menu_keyboard(user_data):
    """
    Keyboard with a button for each ip in the 'computers' array for the
    section.
    Also show a Return button to go back to 'section menu'
    """
    # Get a list with the name and ip for each computers in the JSON,
    # BUT ONLY if the entry has an ip value assigned
    strings = []
    for computer in user_data['bridge_json']['computers']:
        if (computer['ip']):
            strings.append(computer['name'] + ' (' + computer['ip'] + ')')

    # If a single was selected, return button should return to 'department
    # menu'. If a multiple was selected, return button should return to
    # 'section_menu'
    return_label = ""
    if 'department' in user_data:
        return_label = user_data['department']
    else:
        return_label = "Connect"

    return build_keyboard(
        strings,
        n_cols=1,
        footer_buttons=[create_button("Return", return_label)])


def ip_selection_menu(bot, update, user_data):
    query = update.callback_query

    # Save the current section in the user_data
    user_data['section'] = query.data

    # Using the department (if selected) and the section, create a path to the
    # json for the respective section
    json_filepath = 'config/'
    if 'department' in user_data:
        json_filepath += user_data['department'] + '/'
    json_filepath += user_data['section'] + '.json'

    json = helper.open_json_file(json_filepath)

    # Save the json file in user_data. Will be useful for future commands
    user_data['bridge_json'] = json

    query.message.edit_text(
        text=ip_selection_menu_message(user_data),
        reply_markup=ip_selection_menu_keyboard(user_data))


# ##### CONFIRM CONNECTION MENU
def confirm_connection_menu_message(user_data):
    return ("Are you sure that you want to connect to: " +
            user_data['bridge_ip'] + "?")


def confirm_connection_menu_keyboard():
    """Simple Yes or No promt"""
    answers = ["Yes", "No"]
    return build_keyboard(answers, n_cols=2)


def confirm_connection_menu(bot, update, user_data):
    update.message.reply_text(
        text=confirm_connection_menu_message(user_data),
        reply_markup=confirm_connection_menu_keyboard())


# ##### HELPER FUNCTIONS
def build_keyboard(strings, n_cols=2, header_buttons=None,
                   footer_buttons=None):
    """
    Return an InlineKeyboard with sane defaults. callback_data values will be
    the same value as the button labels
    """
    keyboard = [InlineKeyboardButton(s, callback_data=s) for s in strings]

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


# ##### CALLBACKS
def add_menu_callbacks(dp):
    """Add all the callback handlers to the Dispatcher"""
    multiples = []
    sections = []
    singles = []

    # Iterate through all departments. Get an array with all the names and
    # sections
    for department in helper.config['structure']['multiple']:
        multiples.append(department['name'])
        sections.extend(department['sections'])

    for single in helper.config['structure']['single']:
        singles.append(single)

    # Construct a simple regex that match every name
    departments_regex = "|".join(multiples)
    sections_regex = "|".join(sections)
    singles_regex = "|".join(singles)

    # TRIGGERED if a Return to 'main_menu' button is clicked
    dp.add_handler(CallbackQueryHandler(main_menu, pattern="Main"))

    # TRIGGERED if clicked on 'Connect' from 'main_menu', or Return from
    # 'section_menu'
    dp.add_handler(CallbackQueryHandler(department_menu, pattern="Connect",
                                        pass_user_data=True))

    # TRIGGERED if clicked on any department in the 'department_names' array
    dp.add_handler(
        CallbackQueryHandler(
            section_menu, pattern=departments_regex, pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            ip_selection_menu, pattern=singles_regex, pass_user_data=True))

    # TRIGGERED if clicked on any section from the 'section_names' array
    dp.add_handler(
        CallbackQueryHandler(
            ip_selection_menu, pattern=sections_regex, pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(main.connect, pattern="Yes", pass_user_data=True))
    dp.add_handler(CallbackQueryHandler(main_menu, pattern="No"))
