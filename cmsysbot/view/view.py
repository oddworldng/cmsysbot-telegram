from typing import List

from utils import Computer, State

from .keyboard import Button, Keyboard


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
        Button("Update Ips", State.UPDATE_IPS),
        Button("Filter computers", State.FILTER_COMPUTERS),
        Button("Wake computers", State.WAKE_COMPUTERS),
        Button("Shutdown computers", State.SHUTDOWN_COMPUTERS),
        Button("Update computers", State.UPDATE_COMPUTERS),
        Button("Install software", State.INSTALL_SOFTWARE),
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
def yes_no(text: str, yes_callback_data: str,
           no_callback_data: str) -> Keyboard:

    # Buttons
    main_buttons = [
        Button("Yes", yes_callback_data),
        Button("No", no_callback_data)
    ]

    # Keyboard
    return Keyboard(text, n_cols=2, main_buttons=main_buttons)


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
# ---------------------------------
# |       "Return" -> (Main)      |
# ---------------------------------
def filter_computers(computers: List[Computer]):

    # Text
    text = "Select the computers that will be included in future operations"

    main_buttons = [
        Button("Include All", "include-all"),
        Button("Exclude All", "exclude-all")
    ]

    for computer in computers.get_computers():
        main_buttons.append(Button(str(computer)))

        if computer.included:
            main_buttons.append(
                Button("Included", "exclude-%s" % computer.mac))
        else:
            main_buttons.append(
                Button("Excluded", "include-%s" % computer.mac))

    footer_buttons = [Button("Return", State.MAIN)]

    # Keyboard
    return Keyboard(
        text,
        n_cols=2,
        main_buttons=main_buttons,
        footer_buttons=footer_buttons)
