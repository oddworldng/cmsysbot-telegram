import json
from typing import Any, Dict


class BaseJson:
    """
    Base class for all the JSON files used by the program. Has some utilities to load
    JSON files as dictionaries and save them again as files.
    """

    def __init__(self, filepath: str):

        self.data: Dict[str, Any] = {}
        self.filepath: str = filepath

        self.load(filepath)

    # IO methods
    def load(self, filepath: str):
        """Load the .json file as a dictionary that Python can work with"""

        with open(filepath) as json_file:
            self.data = json.load(json_file)

    def save(self):
        """Write the changes made in the dictionary to the .json file"""

        with open(self.filepath, "w") as json_file:
            json.dump(self.data, json_file, indent=2)
