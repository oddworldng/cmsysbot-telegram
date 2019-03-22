from telegram.ext import (Dispatcher, CallbackQueryHandler, MessageHandler,
                          ConversationHandler, Filters, CommandHandler)

from states import State
from controller import menu, callback, conversation, command
import helper


def add_callbacks(dp: Dispatcher):

    with_subsections = []
    without_subsections = []

    for section in helper.config.get_all_sections():
        if section.has_subsections():
            with_subsections.append("^%s$" % section.name)
        else:
            without_subsections.append("^%s$" % section.name)

    with_subsections_regex = "|".join(with_subsections)
    without_subsections_regex = "|".join(without_subsections)

    # Show Main Menu
    dp.add_handler(
        CallbackQueryHandler(
            menu.main, pattern=State.MAIN, pass_user_data=True))

    # Show Connect Menu
    dp.add_handler(
        CallbackQueryHandler(
            menu.select_department, pattern=State.CONNECT, pass_user_data=True))

    # Show structure of department (and subdepartments)
    dp.add_handler(
        CallbackQueryHandler(
            menu.structure, pattern=with_subsections_regex,
            pass_user_data=True))

    # When clicked in a section without subsections, show ip list
    dp.add_handler(
        CallbackQueryHandler(
            menu.ip_selection,
            pattern=without_subsections_regex,
            pass_user_data=True))

    # When clicked on an ip, show the menu asking if continuing the the
    # connection
    dp.add_handler(
        CallbackQueryHandler(
            menu.confirm_connect_ip,
            pattern=State.CONFIRM_CONNECT,
            pass_user_data=True))

    # Triggered when clicking on Disconnect button
    dp.add_handler(
        CallbackQueryHandler(
            callback.disconnect, pattern=State.DISCONNECT, pass_user_data=True))

    # TRIGGERED if clicked on 'Wake Computers from the main menu'
    dp.add_handler(
        CallbackQueryHandler(
            callback.wake_computers,
            pattern=State.WAKE_COMPUTERS,
            pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            callback.shutdown_computers,
            pattern=State.SHUTDOWN_COMPUTERS,
            pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            menu.filter_computers,
            pattern=State.FILTER_COMPUTERS,
            pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            callback.include_computers,
            pattern=State.INCLUDE_COMPUTERS,
            pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            callback.exclude_computers,
            pattern=State.EXCLUDE_COMPUTERS,
            pass_user_data=True))

    ## TRIGGERED if clicked on 'Update Ips' from the main menu
    #dp.add_handler(
    #    CallbackQueryHandler(
    #        main.update_ips, pattern="^Update Ips$", pass_user_data=True))


def add_command_callbacks(dp: Dispatcher):
    dp.add_handler(CommandHandler("start", command.start, pass_user_data=True))


def add_conversation_callbacks(dp: Dispatcher):
    """Add all the conversation handlers to the Dispatcher"""

    # Login handler
    login_conv_handler = ConversationHandler(
        # Entry points: From InlineKeyboardButton or /login
        entry_points=[
            CallbackQueryHandler(
                conversation.login, pattern=State.GET_CREDENTIALS)
        ],
        states={
            conversation.USERNAME: [
                MessageHandler(
                    Filters.text,
                    conversation.get_username,
                    pass_user_data=True)
            ],
            conversation.PASSWORD: [
                MessageHandler(
                    Filters.text,
                    conversation.get_password,
                    pass_user_data=True)
            ],
        },
        fallbacks=[])

    # Add to dispatcher
    dp.add_handler(login_conv_handler)
