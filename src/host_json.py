import json


class HostJson:
    # Constructor
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = None
        self.load(filepath)

    # IO functions
    def load(self, filepath):
        with open(filepath) as json_file:
            self.data = json.load(json_file)

    def save(self):
        with open(self.filepath, 'w') as json_file:
            json.dump(self.data, json_file)

    # Operators
    def add(self, name, ip, mac):
        self.data['computers'].append({'name': name, 'ip': ip, 'mac': mac})
        self.save()

    class Computer:
        def __init__(self, computer_data):
            self.name = ""
            self.ip = ""
            self.mac = ""

            for key in computer_data:
                setattr(self, key, computer_data[key])

        def __str__(self):
            return 'Name: %s Ip: %s Mac: %s' % (self.name, self.ip, self.mac)

        def asdict(self):
            return {'name': self.name, 'ip': self.ip, 'mac': self.mac}

    # Generators
    def get_computers(self):
        for i in range(0, len(self.data['computers'])):
            computer_data = self.data['computers'][i]
            computer = self.Computer(computer_data)

            yield computer

            self.data['computers'][i] = computer.asdict()
