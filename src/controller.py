from telegram.ext import Dispatcher, CallbackQueryHandler

from states import State
import menu
import main
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
            menu.main_menu, pattern=State.MAIN, pass_user_data=True))

    # Show Connect Menu
    dp.add_handler(
        CallbackQueryHandler(
            menu.connect_menu, pattern=State.CONNECT, pass_user_data=True))

    # Show structure of department (and subdepartments)
    dp.add_handler(
        CallbackQueryHandler(
            menu.structure_menu,
            pattern=with_subsections_regex,
            pass_user_data=True))

    # When clicked in a section without subsections, show ip list
    dp.add_handler(
        CallbackQueryHandler(
            menu.ip_selection_menu,
            pattern=without_subsections_regex,
            pass_user_data=True))

    # When clicked on an ip, show the menu asking if continuing the the
    # connection
    dp.add_handler(
        CallbackQueryHandler(
            menu.confirm_connect_ip_menu,
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
