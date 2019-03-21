class State():
    MAIN = "main"
    CONNECT = "connect"
    CONFIRM_CONNECT = "^[\d*\.*]*$"  # TODO: Make a better regex
    GET_CREDENTIALS = "get-credentials"
    DISCONNECT = "disconnect"
    WAKE_COMPUTERS = "wake-computers"
    SHUTDOWN_COMPUTERS = "shutdown-computers"
