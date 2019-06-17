import json
from typing import Any, Dict, Iterator, List, Union

from .base_json import BaseJson


class Computer:
    """
    This class represents a computer. Provides getters and setters to avoid interacting
    directly with the dictionary
    """

    def __init__(self, computer_data: Dict[str, Union[str, bool]] = {}):
        """
        Create a "Computer" object with default values, or with values read from a
        Dictionary.
        """

        # Initialize with N/A string to avoid having empty strings
        self.name: str = "N/A"
        self.ip: str = "N/A"
        self.mac: str = "N/A"
        self.included: bool = True

        # If a dictionary is passed, save the keys (name, ip, mac...) as attributes
        # values
        for key in computer_data:
            try:
                getattr(self, key)
                setattr(self, key, computer_data[key])
            except AttributeError:
                pass

    def __str__(self) -> str:
        """Return the Computer object as a string for identification."""

        return f"{self.name} ({self.ip})"

    def asdict(self) -> dict:
        """
        Return the Computer as a Dict object (useful for writing it to a JSON file)

        NOTE: The attribute 'included' has been left out on purpose, as it shouldn't be
        saved on the JSON file.
        """

        return {"name": self.name, "ip": self.ip, "mac": self.mac}


class Computers(BaseJson):
    """
    This class provides an interface for using the .json files created on config/ (not
    config.json). Provides functions to get the names/ips/macs of the computers and
    easily save changes on the .json
    """

    def __init__(self, filepath: str):
        """
        Load the .json from an existent file. Throws if couldn't open/read the file
        """

        self.__index = 0

        super().__init__(filepath)

        # Transform dict to array of Computer objects
        self.computers: List[Computer] = [
            Computer(entry) for entry in self.data["computers"]
        ]

    def save(self):
        """
        Transform each Computer object to a Dict and write the changes to the file.
        """

        # TODO: Really necessary or doing the conversion twice?
        self.data["computers"] = [computer.asdict() for computer in self.computers]

        super().save()

    @staticmethod
    def create(filepath: str):
        """Create a .json file with the basic scheme."""

        with open(filepath, "w") as outfile:
            json_scheme: Dict[str, List] = {}
            json_scheme["computers"] = []

            json_scheme["computers"].append(Computer().asdict())
            json.dump(json_scheme, outfile, indent=2)

            return json_scheme

        return None

    # Operators
    def add(self, name: str, ip: str, mac: str):
        """
        Add a new computer. NOTE: Changes are only made in the dictionary. To make the
        changes permanent in the .json file, use save() afterwards
        """

        self.data["computers"].append({"name": name, "ip": ip, "mac": mac})

    def remove(self, mac: str):
        """
        Remove a computer with the same mac value. If the computer to be removed is not
        found, it does nothing. NOTE: Changes are only made in the dictionary. To make
        the changes permanent in the .json file, use save() afterwards
        """

        for i, computer in enumerate(self.get_computers()):
            if computer.mac == mac:
                del self.data["computers"][i]
                break

    def find(self, mac: str) -> Union[Computer, None]:
        """
        Find and return the first computer found with the same MAC address. Returns
        "None" if couldn't find a computer.
        """

        for computer in self.get_computers():
            if computer.mac == mac:
                return computer

        return None

    def __len__(self):
        """Return the number of computers defined on the config file"""

        return len(self.data["computers"])

    # Generators
    def __iter__(self):
        """Iterate through all the computer objects using the class as an Iterator"""
        return self.get_computers()

    def get_computers(self) -> Iterator[Computer]:
        """Yield Computer objects."""

        for computer in self.computers:
            yield computer

    def get_included(self):
        """Alias for `get_included_computers()`"""
        return self.get_included_computers()

    def get_included_computers(self) -> Iterator[Computer]:
        """Yield only Computer objects where "included" is true."""

        for computer in self.computers:
            if computer.included:
                yield computer

    def get_names(self) -> Iterator[str]:
        """
        DEPRECATED. Use map() with a lambda function instead.

        Yield the name of each computer.
        """

        for computer in self.get_computers():
            yield computer.name

    def get_ips(self) -> Iterator[str]:
        """
        DEPRECATED. Use map() with a lambda function instead.

        Yield the ip of each computer.
        """

        for computer in self.get_computers():
            yield computer.ip

    def get_macs(self) -> Iterator[str]:
        """
        DEPRECATED. Use map() with a lambda function instead.

        Yield the mac of each computer.
        """

        for computer in self.get_computers():
            yield computer.mac
