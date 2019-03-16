import json


class Computers:
    """This class provides an interface for using the .json files created on
    config/ (not config.json). Provides functions to get the names/ips/macs of
    the computers and easily save changes on the .json"""

    def __init__(self, filepath: str):
        """Load the .json from an existent file. Throws if couldn't open/read
        the file"""

        self.filepath = filepath
        self.data = None
        self.load(filepath)

    # IO methods
    def load(self, filepath: str):
        """Load the .json file as a dictionary that Python can work with"""

        with open(filepath) as json_file:
            self.data = json.load(json_file)

    def save(self):
        """Write the changes made in the dictionary to the .json file"""

        with open(self.filepath, 'w') as json_file:
            json.dump(self.data, json_file)

    class Computer:
        """This class represents a computer. Provides getters and setters to
        avoid interacting directly with the dictionary"""

        def __init__(self, computer_data: dict = {}):
            # Initialize with N/A string to avoid having empty strings
            self.name = "N/A"
            self.ip = "N/A"
            self.mac = "N/A"

            # If a dictionary is passed, save the keys as attributes only if
            # they're not empty
            for key in computer_data:
                if (computer_data[key]):
                    setattr(self, key, computer_data[key])

        def __str__(self):
            return 'Name: %s Ip: %s Mac: %s' % (self.name, self.ip, self.mac)

        def asdict(self):
            return {'name': self.name, 'ip': self.ip, 'mac': self.mac}

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

    # Generators
    def get_computers(self) -> Computer:
        """Yield a Computer object for each element in the .json 'computers'
        array. The element returned CAN BE MODIFIED. The changes will be
        reflected in the dictionary"""

        for i in range(0, len(self.data['computers'])):
            computer_data = self.data['computers'][i]
            computer = self.Computer(computer_data)

            yield computer

            self.data['computers'][i] = computer.asdict()

    def get_names(self) -> str:
        """Yield the name of each computer"""

        for computer in self.get_computers():
            yield computer.name

    def get_ips(self) -> str:
        """Yield the ip of each computer"""
        for computer in self.get_computers():
            yield computer.ip

    def get_macs(self) -> str:
        """Yield the mac of each computer"""
        for computer in self.get_computers():
            yield computer.mac
