import os
import json
import computers_json


class Config:
    def __init__(self, filepath: str):
        """Load the .json from an existent file. Throws if couldn't open/read
        the file"""

        self.filepath = filepath
        self.root_folder = os.path.dirname(filepath) + "/"

        self.data = None
        self.load(filepath)

        self._create_folder_structure()

    # IO methods
    def load(self, filepath: str):
        """Load the .json file as a dictionary that Python can work with"""

        with open(filepath) as json_file:
            self.data = json.load(json_file)

    def save(self):
        """Write the changes made in the dictionary to the .json file"""

        with open(self.filepath, 'w') as json_file:
            json.dump(self.data, json_file)

    @property
    def token(self) -> str:
        return self.data['token']

    @property
    def name(self) -> str:
        return self.data['name']

    @property
    def email(self) -> str:
        return self.data['email']

    class Section:
        def __init__(self, section_data):
            self.name = "N/A"
            self.subsections = []

            # Initialiize Section from a string
            if type(section_data) is str:
                self.name = section_data

            # Initialize Section from a dict
            elif type(section_data) is dict:
                if 'name' in section_data:
                    self.name = section_data['name']

                if 'sections' in section_data:
                    self.subsections = section_data['sections']

        def has_subsections(self):
            return self.subsections

        def len(self):
            return len(self.subsections)

    def get_sections(self, route=[]):
        sections = [self.Section(s) for s in self.data['structure']]

        for part in route:
            for section in sections:
                if part == section.name and section.has_subsections():
                    sections = [self.Section(s) for s in section.subsections]
                    break

        for section in sections:
            yield section

    def get_all_sections(self, route=[]):
        for section in self.get_sections(route):
            yield section

            if section.has_subsections():
                route.append(section.name)
                yield from self.get_all_sections(route)
                route.pop()

    def get_sections_with_subsections(self):
        for section in self.get_all_sections():
            if section.has_subsections():
                yield section.name

    def get_sections_without_subsections(self):
        for section in self.get_all_sections():
            if not section.has_subsections():
                yield section.name

    def _create_folder_structure(self, route=[]):
        for section in self.get_sections(route):
            if section.has_subsections():
                self._create_folder(route + [section.name])

                route.append(section.name)
                self._create_folder_structure(route)
                route.pop()
            else:
                self._create_file(route + [section.name])

    def _create_folder(self, route):
        folder_path = self.root_folder + "/".join(route)

        if not os.path.isdir(folder_path):
            print("> Create directory", folder_path)
            os.makedirs(folder_path)

    def _create_file(self, route):
        file_path = self.root_folder + "/".join(route) + ".json"

        if not os.path.exists(file_path):
            print("> Create file", file_path)
            computers_json.Computers.create(file_path)
