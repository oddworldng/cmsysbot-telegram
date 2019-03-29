config_file = None

class State():
    MAIN = "main"
    CONNECT = "connect"
    CONFIRM_CONNECT = "^[\d*\.*]*$"  # TODO: Make a better regex
    GET_CREDENTIALS = "get-credentials"
    DISCONNECT = "disconnect"
    WAKE_COMPUTERS = "wake-computers"
    SHUTDOWN_COMPUTERS = "shutdown-computers"
    FILTER_COMPUTERS = "filter-computers"
    INCLUDE_COMPUTERS = "include-(.*)"
    EXCLUDE_COMPUTERS = "exclude-(.*)"
    UPDATE_IPS = "update-ips"
    UPDATE_COMPUTERS = "update-computers"
    INSTALL_SOFTWARE = "install-software"
