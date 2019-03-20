class State():
    MAIN = "Main"
    CONNECT = "Connect"
    CONFIRM_CONNECT = "^[\d*\.*]*$" # TODO: Fix regex
    GET_CREDENTIALS = "Get_Credentials"
    DISCONNECT = "Disconnect"
