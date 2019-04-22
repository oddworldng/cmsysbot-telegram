config_file = None


class State:
    MAIN = "main"
    CONNECT = "connect"
    CONFIRM_CONNECT = r"^[\d*\.*]*$"  # TODO: Make a better regex
    GET_CREDENTIALS = "get-credentials"
    DISCONNECT = "disconnect"
    FILTER_COMPUTERS = "filter-computers"
    INCLUDE_COMPUTERS = "include-(.*)"
    EXCLUDE_COMPUTERS = "exclude-(.*)"
    UPDATE_IPS = "update-ips"
    START_PLUGIN = "plugin-(.*)"
