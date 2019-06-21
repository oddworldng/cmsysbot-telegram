"""
In this module are defined all the ``Handlers`` used by the
bot.

Note:
    A :obj:`Handler` is an object from the python-teelgram-bot library. It does
    all the connection between the user actions and the python functions that
    should be called (For example, a Handler that states that when receiving
    /start, the function menu.main should be called...)
"""

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Dispatcher,
    Filters,
    MessageHandler,
    RegexHandler,
)

from cmsysbot.utils import State, states

from . import command, conversation, general, menu


def add_callbacks(dp: Dispatcher):
    """
    Register all the callbacks defined in :mod:`cmsysbot.controller.menu`
    and :mod:`cmsysbot.controller.general`

    Args:
        dp (:obj:`telegram.ext.Dispatcher`): Telegram object that registers all
        handlers.
    """

    # Show Main Menu
    dp.add_handler(
        CallbackQueryHandler(menu.main, pattern=State.MAIN, pass_user_data=True)
    )

    # Show Connect Menu
    dp.add_handler(
        CallbackQueryHandler(
            menu.select_department, pattern=State.CONNECT, pass_user_data=True
        )
    )

    # Settings for the structure menu:
    with_subsections = []
    without_subsections = []

    for section in states.config_file.get_all_sections():
        if section.has_subsections():
            with_subsections.append(f"^{section.name}$")
        else:
            without_subsections.append(f"^{section.name}$")

    # On the structure menu (when selecting a department/subsection), the
    # returned value after clicking on a button will be the name of the
    # section, so a regex that matches all the possible section names must be
    # crafted.
    #
    # For example, given the following structure:
    # OSL
    #  \- A
    #  \- B
    #     \- C
    #
    # The content of the regex will be:
    # with_subsections_regex = OSL|B
    # without_subsections_regex = A|C
    #
    # So, if we click on 'OSL', the callback return  data will be 'OSL', which
    # matches the `with_subsections_regex`. This pattern is associated to the
    # function menu.structure, which then shows the subsections for 'OSL'
    # On the other hand, if we click on 'A', which doesn't has any subsections,
    # the return data from the callback ('A') will match
    # `withouth_subsections_regex`, calling the function `menu.ip_selection`
    # instead.

    with_subsections_regex = "|".join(with_subsections)
    without_subsections_regex = "|".join(without_subsections)

    # Show structure of department (and subdepartments)
    dp.add_handler(
        CallbackQueryHandler(
            menu.structure, pattern=with_subsections_regex, pass_user_data=True
        )
    )

    # When clicked in a section without subsections, show ip list
    dp.add_handler(
        CallbackQueryHandler(
            menu.ip_selection, pattern=without_subsections_regex, pass_user_data=True
        )
    )

    # When clicked on an ip, show a menu asking if it should continue with
    # the connection
    dp.add_handler(
        CallbackQueryHandler(
            menu.confirm_connect_ip, pattern=State.CONFIRM_CONNECT, pass_user_data=True
        )
    )

    # Triggered when clicking on Disconnect button from main menu.
    dp.add_handler(
        CallbackQueryHandler(
            general.disconnect, pattern=State.DISCONNECT, pass_user_data=True
        )
    )

    # Show menu for filtering computers
    dp.add_handler(
        CallbackQueryHandler(
            menu.filter_computers, pattern=State.FILTER_COMPUTERS, pass_user_data=True
        )
    )

    # Triggered when clicking on the Include button from the filter computers
    # menu
    dp.add_handler(
        CallbackQueryHandler(
            general.include_computers,
            pattern=State.INCLUDE_COMPUTERS,
            pass_user_data=True,
        )
    )

    # Triggered when clicking on the Exclude button from the filter computers
    # menu
    dp.add_handler(
        CallbackQueryHandler(
            general.exclude_computers,
            pattern=State.EXCLUDE_COMPUTERS,
            pass_user_data=True,
        )
    )

    # Triggered when clicking on the Update Ips button from the main menu
    dp.add_handler(
        CallbackQueryHandler(
            general.update_ips, pattern=State.UPDATE_IPS, pass_user_data=True
        )
    )


def add_command_callbacks(dp: Dispatcher):
    """
    Register all the command callbacks defined in
    :mod:`cmsysbot.controller.command`

    Args:
        dp (:obj:`telegram.ext.Dispatcher`): Telegram object that registers all
        handlers.
    """

    # Triggered when sending '/start' to the bot
    dp.add_handler(CommandHandler("start", command.start, pass_user_data=True))


def add_conversation_callbacks(dp: Dispatcher):
    """
    Register all the callbacks defined in
    :mod:`cmsysbot.controller.conversation`

    Args:
        dp (:obj:`telegram.ext.Dispatcher`): Telegram object that registers all
        handlers.
    """

    # Login handler
    login_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(conversation.login, pattern=State.GET_CREDENTIALS)
        ],
        states={
            conversation.USERNAME: [
                MessageHandler(
                    Filters.text, conversation.get_username, pass_user_data=True
                )
            ],
            conversation.PASSWORD: [
                MessageHandler(
                    Filters.text, conversation.get_password, pass_user_data=True
                )
            ],
        },
        fallbacks=[RegexHandler("^/cancel$", menu.new_main, pass_user_data=True)],
        allow_reentry=True,
    )

    plugin_exec_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                conversation.start_plugin_from_callback,
                pattern=State.START_PLUGIN,
                pass_user_data=True,
            ),
            MessageHandler(
                Filters.document,
                conversation.start_plugin_from_download,
                pass_user_data=True,
            ),
        ],
        states={
            conversation.ANSWER: [
                MessageHandler(
                    Filters.text, conversation.get_answer, pass_user_data=True
                )
            ]
        },
        fallbacks=[RegexHandler("^/cancel$", menu.new_main, pass_user_data=True)],
        allow_reentry=True,
    )

    # Add to dispatcher
    dp.add_handler(login_conv_handler)
    dp.add_handler(plugin_exec_handler)
