from typing import List

from keyboard import Button, Keyboard
from computers_json import Computer

from states import State

# Status: Not Connected
# ---------------------------------
# |  "Connnect" -> (Departments)  |
# ---------------------------------


def not_connected_view() -> Keyboard:
    # Text
    text = "Status: Not Connected"

    # Buttons
    main_buttons = [Button("Connect", State.CONNECT)]

    # Keyboard
    return Keyboard(text, main_buttons=main_buttons)


# Route: ESIT/A/B/...
# Select your department
# ---------------- ----------------
# |      OSL     | |     ESIT     |
# ---------------- ----------------
# ---------------------------------
# |       "Return" -> (Main)      |
# ---------------------------------


def structure_view(route: List[str], sections: List[Computer],
                   return_to: str) -> Keyboard:
    # Text
    text = "Select the section to connect\n"
    text += "Route: %s" % "/".join(route)

    # Buttons
    main_buttons = [Button(section.name) for section in sections]
    footer_buttons = [Button("Return", return_to)]

    # Keyboard
    return Keyboard(
        text,
        n_cols=2,
        main_buttons=main_buttons,
        footer_buttons=footer_buttons)


# Route: ESIT/A/B/...
# Now, select your bridge computer
# ---------------------------------
# |  Name: E1. Ip: 192.168.1.10   |
# ---------------------------------
# ---------------------------------
# |  Name: E2. Ip: 192.168.1.13   |
# ---------------------------------


def ip_selection_view(route: List[str], computers: List[Computer],
                      return_to: str) -> Keyboard:
    # Text
    text = "Route: %s" % "/".join(route)
    text += "\nNow, select a 'bridge' computer for the local connection"

    # Buttons
    main_buttons = [
        Button(str(computer), computer.ip) for computer in computers
    ]
    footer_buttons = [Button("Return", return_to)]

    # Keyboard
    return Keyboard(
        text, main_buttons=main_buttons, footer_buttons=footer_buttons)


# [text]
# ---------------- ----------------
# |      Yes     | |      No      |
# ---------------- ----------------


def yes_no_menu(text: str, yes_callback_data: str, no_callback_data: str):

    # Buttons
    main_buttons = [
        Button("Yes", yes_callback_data),
        Button("No", no_callback_data)
    ]

    # Keyboard
    return Keyboard(text, n_cols=2, main_buttons=main_buttons)
