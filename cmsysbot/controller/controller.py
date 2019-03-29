from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Dispatcher, Filters,
                          MessageHandler)

from utils import State, states

from . import command, conversation, general, menu


def add_callbacks(dp: Dispatcher):

    with_subsections = []
    without_subsections = []

    for section in states.config_file.get_all_sections():
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
            menu.select_department, pattern=State.CONNECT,
            pass_user_data=True))

    # Show structure of department (and subdepartments)
    dp.add_handler(
        CallbackQueryHandler(
            menu.structure,
            pattern=with_subsections_regex,
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
            menu.disconnect, pattern=State.DISCONNECT, pass_user_data=True))

    # TRIGGERED if clicked on 'Wake Computers from the main menu'
    dp.add_handler(
        CallbackQueryHandler(
            general.wake_computers,
            pattern=State.WAKE_COMPUTERS,
            pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            general.shutdown_computers,
            pattern=State.SHUTDOWN_COMPUTERS,
            pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            menu.filter_computers,
            pattern=State.FILTER_COMPUTERS,
            pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            general.exclude_computers,
            pattern=State.EXCLUDE_COMPUTERS,
            pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            general.include_computers,
            pattern=State.INCLUDE_COMPUTERS,
            pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            general.update_ips, pattern=State.UPDATE_IPS, pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            general.update_computers,
            pattern=State.UPDATE_COMPUTERS,
            pass_user_data=True))

    dp.add_handler(
        CallbackQueryHandler(
            general.execute_plugin,
            pattern=State.EXECUTE_PLUGIN,
            pass_user_data=True))

    dp.add_handler(
        MessageHandler(
            Filters.document, general.download_script, pass_user_data=True))


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

    # Install software handler
    install_software_handler = ConversationHandler(
        # Entry points: From InlineKeyboardButton or /login
        entry_points=[
            CallbackQueryHandler(
                conversation.software, pattern=State.INSTALL_SOFTWARE)
        ],
        states={
            conversation.SOFTWARE: [
                MessageHandler(
                    Filters.text,
                    conversation.get_software,
                    pass_user_data=True)
            ]
        },
        fallbacks=[])

    # Add to dispatcher
    dp.add_handler(login_conv_handler)
    dp.add_handler(install_software_handler)
