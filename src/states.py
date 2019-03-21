class State():
    MAIN = "Main"
    CONNECT = "Connect"
    CONFIRM_CONNECT = "^[\d*\.*]*$"  # TODO: Make a better regex
    GET_CREDENTIALS = "Get_Credentials"
    DISCONNECT = "Disconnect"
    WAKE_COMPUTERS = "WOL"
