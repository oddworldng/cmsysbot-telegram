from typing import List

from utils.computers_json import Computer

from states import State
from view.keyboard import Button, Keyboard
from utils.session import Session

# Status: Not Connected
# ---------------------------------
# |  "Connnect" -> (Departments)  |
# ---------------------------------


def not_connected() -> Keyboard:
    # Text
    text = "Status: Not Connected"

    # Buttons
    main_buttons = [Button("Connect", State.CONNECT)]

    # Keyboard
    return Keyboard(text, main_buttons=main_buttons)


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
def connected(route: List[str], username: str, bridge_ip: str) -> Keyboard:
    # Text
    text = "Status: Connected\n"
    text += "Route: %s\n" % "/".join(route)
    text += "Username: %s\n" % username
    text += "Bridge ip: %s\n" % bridge_ip

    # Buttons
    main_buttons = [
        Button("Update Ips"),
        Button("Filter computers"),
        Button("Wake computers"),
        Button("Shutdown computers"),
        Button("Update computers"),
        Button("Install software"),
        Button("Execute script"),
        Button("Upload file")
    ]

    footer_buttons = [Button("Disconnect", State.DISCONNECT)]

    # Keyboard
    return Keyboard(
        text,
        n_cols=2,
        main_buttons=main_buttons,
        footer_buttons=footer_buttons)


# Route: ESIT/A/B/...
# Select your department
# ---------------- ----------------
# |      OSL     | |     ESIT     |
# ---------------- ----------------
# ---------------------------------
# |       "Return" -> (Main)      |
# ---------------------------------


def structure(route: List[str], sections: List[Computer],
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


def ip_selection(route: List[str], computers: List[Computer],
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


def yes_no(text: str, yes_callback_data: str, no_callback_data: str):

    # Buttons
    main_buttons = [
        Button("Yes", yes_callback_data),
        Button("No", no_callback_data)
    ]

    # Keyboard
    return Keyboard(text, n_cols=2, main_buttons=main_buttons)


def disconnect() -> str:
    return "Disconnected."
