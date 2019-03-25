import json
from typing import Iterator

from .base_json import Json


class Computer:
    """This class represents a computer. Provides getters and setters to
    avoid interacting directly with the dictionary"""

    def __init__(self, computer_data: dict = None):
        computer_data = computer_data or {}

        # Initialize with N/A string to avoid having empty strings
        self.name = "N/A"
        self.ip = "N/A"
        self.mac = "N/A"
        self.included = True

        # If a dictionary is passed, save the keys as attributes only if
        # they're not empty
        if computer_data:
            for key in computer_data:
                if (computer_data[key]):
                    setattr(self, key, computer_data[key])

    def __str__(self) -> str:
        return 'Name: %s Ip: %s Mac: %s' % (self.name, self.ip, self.mac)

    def asdict(self) -> dict:
        return {'name': self.name, 'ip': self.ip, 'mac': self.mac}


class Computers(Json):
    """This class provides an interface for using the .json files created on
    config/ (not config.json). Provides functions to get the names/ips/macs of
    the computers and easily save changes on the .json"""

    def __init__(self, filepath: str):
        """Load the .json from an existent file. Throws if couldn't open/read
        the file"""
        super().__init__(filepath)

        # Transform dict to array of Computer objects
        self.computers = [Computer(entry) for entry in self.data['computers']]

    def save(self):
        self.data['computers'] = [
            computer.asdict() for computer in self.computers
        ]

        super().save()

    @staticmethod
    def create(filepath: str):
        """Create a .json file with the basic scheme"""

        with open(filepath, "w") as outfile:
            json_scheme = {}
            json_scheme['computers'] = []
            json_scheme['computers'].append({
                'name': "N/A",
                'ip': "N/A",
                'mac': "N/A"
            })
            json.dump(json_scheme, outfile)

    # Operators
    def add(self, name: str, ip: str, mac: str):
        """Add a new computer. NOTE: Changes are only made in the dictionary. To
        make the changes permanent in the .json file, use save() afterwards"""

        self.data['computers'].append({'name': name, 'ip': ip, 'mac': mac})

    def remove(self, mac: str):
        """Remove a computer with the same mac value. If the computer to be
        removed is not found, does nothing. NOTE: Changes are only made in the
        dictionary. To make the changes permanent in the .json file, use save()
        afterwards"""

        for i, computer in enumerate(self.get_computers()):
            if (computer.mac == mac):
                del self.data['computers'][i]
                break

    def find(self, mac: str):
        for computer in self.get_computers():
            if computer.mac == mac:
                return computer

    # Generators
    def get_computers(self) -> Iterator[Computer]:
        for computer in self.computers:
            yield computer

    def get_included_computers(self) -> Iterator[Computer]:
        for computer in self.computers:
            if computer.included:
                yield computer

    def get_names(self) -> Iterator[str]:
        """Yield the name of each computer"""

        for computer in self.get_computers():
            yield computer.name

    def get_ips(self) -> Iterator[str]:
        """Yield the ip of each computer"""

        for computer in self.get_computers():
            yield computer.ip

    def get_macs(self) -> Iterator[str]:
        """Yield the mac of each computer"""

        for computer in self.get_computers():
            yield computer.mac
