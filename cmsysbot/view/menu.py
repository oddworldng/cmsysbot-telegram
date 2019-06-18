"""
In this module are defined all the menus (text + keyboard) created by the bot.
For views that are text only, see the module :mod:`cmsysbot.view.message`.
"""

from typing import Dict, List

from cmsysbot.utils import Computer, State

from .keyboard import Button, Keyboard


def not_connected() -> Keyboard:
    """
    .. code-block:: python

        # Status: Not Connected
        # ---------------------------------
        # |        "Connnect"             |
        # ---------------------------------

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = "Status: Not Connected"

    # Buttons
    main_buttons = [Button("Connect", State.CONNECT)]

    # Keyboard
    return Keyboard(text, main_buttons=main_buttons)


def connected(
    route: List[str], plugins: Dict[str, str], username: str, bridge_ip: str
) -> Keyboard:
    """
    .. code-block:: python

        # Status: Connected
        # Route: [route]
        # Username: [username]
        # Bridge ip: [bridge_ip]
        # ---------------- ----------------
        # |  Update Ips  | | Filter comp. |
        # ---------------- ----------------
        # ---------------- ----------------
        # |  Wake comp.  | | Shutd. comp. |
        # ---------------- ----------------
        #               . . .
        # ---------------------------------
        # |          Disconnect           |
        # ---------------------------------

    Args:
        route (:obj:`List[str]`): Selected path (structure/substructure/...)
        plugins (:obj:`Dict[str, str]`): Names and callback_data for each
            defined plugin.
        username (:obj:`str`): Username
        bridge_ip (:obj:`str`): Ip of the bridge computer

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = "Status: Connected\n"
    text += "Route: %s\n" % "/".join(route)
    text += "Username: %s\n" % username
    text += "Bridge ip: %s\n" % bridge_ip

    # Buttons
    main_buttons = [
        Button("Update ips", State.UPDATE_IPS),
        Button("Filter computers", State.FILTER_COMPUTERS),
    ]

    main_buttons.extend([Button(value, key) for key, value in plugins.items()])

    footer_buttons = [Button("Disconnect", State.DISCONNECT)]

    # Keyboard
    return Keyboard(
        text, n_cols=2, main_buttons=main_buttons, footer_buttons=footer_buttons
    )


def structure(route: List[str], sections: List[str], return_to: str) -> Keyboard:
    """
    .. code-block:: python

        # Route: ESIT/A/B/...
        # Select your department
        # ---------------- ----------------
        # |      OSL     | |     ESIT     |
        # ---------------- ----------------
        #                ...
        # ---------------------------------
        # |            "Return"           |
        # ---------------------------------

    Args:
        route (:obj:`List[str]`): Selected path (structure/substructure/...)
        sections (:obj:`List[Computer]`): List of the sections for the current
            route
        return_to (:obj:`str`): Callback data value for the return button

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = "Select the section to connect\n"
    text += "Route: %s" % "/".join(route)

    # Buttons
    main_buttons = [Button(section.name) for section in sections]
    footer_buttons = [Button("Return", return_to)]

    # Keyboard
    return Keyboard(
        text, n_cols=2, main_buttons=main_buttons, footer_buttons=footer_buttons
    )


def ip_selection(
    route: List[str], computers: List[Computer], return_to: str
) -> Keyboard:
    """
    .. code-block:: python

        # Route: ESIT/A/B/...
        # Now, select your bridge computer
        # ---------------------------------
        # |  Name: E1. Ip: 192.168.1.10   |
        # ---------------------------------
        # ---------------------------------
        # |  Name: E2. Ip: 192.168.1.13   |
        # ---------------------------------
        #               ...
        # ---------------------------------
        # |            "Return"           |
        # ---------------------------------

    Args:
        route (:obj:`List[str]`): Selected path (structure/substructure/...)
        computers(:obj:`List[Computer]`): List of the computers on the current
            section
        return_to (:obj:`str`): Callback data value for the return button

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = "Route: %s" % "/".join(route)
    text += "\nNow, select a 'bridge' computer for the local connection"

    # Buttons
    main_buttons = [Button(str(computer), computer.ip) for computer in computers]
    footer_buttons = [Button("Return", return_to)]

    # Keyboard
    return Keyboard(text, main_buttons=main_buttons, footer_buttons=footer_buttons)


def yes_no(text: str, yes_callback_data: str, no_callback_data: str) -> Keyboard:
    """
    .. code-block:: python

        # [text]
        # ---------------- ----------------
        # |      Yes     | |      No      |
        # ---------------- ----------------

    Args:
        text (:obj:`str`): Text of the keyboard
        yes_callback_data(:obj:`str`): Callback to call after clicking on the
            yes button
        no_callback_data(:obj:`str`): Callback to call after clicking on the
            no button

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Buttons
    main_buttons = [Button("Yes", yes_callback_data), Button("No", no_callback_data)]

    # Keyboard
    return Keyboard(text, n_cols=2, main_buttons=main_buttons)


def filter_computers(computers: List[Computer]):
    """
    .. code-block:: python

        # Select the computers that will be
        # included in future operations
        # ---------------- ----------------
        # |   Inc. All   | |  Excl. All   |
        # ---------------- ----------------
        # --------------------------- -----
        # |   Name: E1. Ip: 191...  | | V |
        # --------------------------- -----
        # --------------------------- -----
        # |   Name: E2. Ip: 191...  | | X |
        # --------------------------- -----
        # --------------------------- -----
        # |   Name: E3. Ip: 191...  | | X |
        # --------------------------- -----
        #               ...
        # ---------------------------------
        # |            "Return"           |
        # ---------------------------------

    Args:
        computer(:obj:`List[Computer]`): List of computers to show as buttons.

    Returns:
        :obj:`cmsysbot.view.keyboard.Keyboard`
    """

    # Text
    text = "Select the computers that will be included in future operations"

    # Buttons
    main_buttons = [
        Button("Include All", "include-all"),
        Button("Exclude All", "exclude-all"),
    ]

    # Add the buttons according to the computer attributes
    for computer in computers.get_computers():
        main_buttons.append(Button(str(computer)))

        if computer.included:
            main_buttons.append(Button("Included", "exclude-%s" % computer.mac))
        else:
            main_buttons.append(Button("Excluded", "include-%s" % computer.mac))

    footer_buttons = [Button("Return", State.MAIN)]

    # Keyboard
    return Keyboard(
        text, n_cols=2, main_buttons=main_buttons, footer_buttons=footer_buttons
    )
