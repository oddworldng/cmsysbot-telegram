from wakeonlan import send_magic_packet

from typing import List


def wake_on_lan(target_mac: str):
    send_magic_packet(target_mac)
