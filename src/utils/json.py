import json


class Json:
    def __init__(self, filepath: str):
        self.data = None
        self.filepath = filepath
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
