from keyboard import Button, Keyboard

from states import State


# Status: Not Connected
# ---------------------------------
# |  "Connnect" -> (Departments)  |
# ---------------------------------

def not_connected_view(message):
    text = "Status: Not Connected"

    main_buttons = [Button("Connect", State.DEPARTMENTS)]

    Keyboard(message, text, main_buttons=main_buttons)


# Select your department
# ---------------- ----------------
# |      OSL     | |     ESIT     |
# ---------------- ----------------
# ---------------------------------
# |       "Return" -> (Main)      |
# ---------------------------------

def structure_view(message, text, sections, return_to):
    main_buttons = [Button(sec_name) for sec_name in sections]
    footer_buttons = [Button("Return", return_to)]

    Keyboard(message, text, n_cols=2, main_buttons=main_buttons,
             footer_buttons=footer_buttons)


# Now, select your bridge computer
# ---------------------------------
# |  Name: E1. Ip: 192.168.1.10   |
# ---------------------------------
# ---------------------------------
# |  Name: E2. Ip: 192.168.1.13   |
# ---------------------------------

def ip_selection_view(message, computers, return_to):
    text = "Now, select a 'bridge computer for the local connection"

    main_buttons = [Button(str(computer), computer.ip)
                    for computer in computers]

    footer_buttons = [Button("Return", return_to)]

    Keyboard(message, text, main_buttons=main_buttons,
             footer_buttons=footer_buttons)
