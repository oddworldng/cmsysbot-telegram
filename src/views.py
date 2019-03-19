from keyboard import Button, Keyboard

from states import State

# Status: Not Connected
# ---------------------------------
# |  "Connnect" -> (Departments)  |
# ---------------------------------


def not_connected_view(message):
    text = "Status: Not Connected"

    main_buttons = [Button("Connect", State.CONNECT)]

    Keyboard(message, text, main_buttons=main_buttons)


# Route: ESIT/A/B/...
# Select your department
# ---------------- ----------------
# |      OSL     | |     ESIT     |
# ---------------- ----------------
# ---------------------------------
# |       "Return" -> (Main)      |
# ---------------------------------


def structure_view(message, route, sections, return_to):
    text = "Select the section to connect\n"
    text += "Route: %s" % "/".join(route)

    main_buttons = [Button(section.name) for section in sections]
    footer_buttons = [Button("Return", return_to)]

    Keyboard(
        message,
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


def ip_selection_view(message, route, computers, return_to):
    text = "Route: %s" % "/".join(route)
    text += "\nNow, select a 'bridge' computer for the local connection"

    main_buttons = [
        Button(str(computer), computer.ip) for computer in computers
    ]

    footer_buttons = [Button("Return", return_to)]

    Keyboard(
        message, text, main_buttons=main_buttons, footer_buttons=footer_buttons)
