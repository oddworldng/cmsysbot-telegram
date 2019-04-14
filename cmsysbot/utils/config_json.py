import os
from typing import Iterator, List, Union

from .base_json import BaseJson
from .computers_json import Computers


class Section:
    def __init__(self, section_data: Union[str, dict]):
        self.name = "N/A"
        self.subsections = []

        # Initialiize Section from a string
        if isinstance(section_data, str):
            self.name = section_data

        # Initialize Section from a dict
        elif isinstance(section_data, dict):
            if 'name' in section_data:
                self.name = section_data['name']

            if 'sections' in section_data:
                self.subsections = section_data['sections']

    def has_subsections(self):
        return self.subsections

    def len(self):
        return len(self.subsections)

    def __str__(self):
        return "%s: %s" % (self.name, self.subsections)


class Config(BaseJson):
    def __init__(self, filepath: str):
        """Load the .json from an existent file. Throws if couldn't open/read
        the file"""

        super().__init__(filepath)

        self.root_folder = os.path.dirname(filepath) + "/"
        self._create_folder_structure()

    @property
    def token(self) -> str:
        return self.data['token']

    @property
    def bot_name(self) -> str:
        return self.data['name']

    @property
    def email(self) -> str:
        return self.data['email']

    @property
    def server_tmp_dir(self) -> str:
        return self.data['server_tmp_dir']

    @property
    def bridge_tmp_dir(self) -> str:
        return self.data['bridge_tmp_dir']

    @property
    def remote_tmp_dir(self) -> str:
        return self.data['remote_tmp_dir']

    @property
    def log_dir(self) -> str:
        return self.data['log_dir']

    @property
    def plugins_dir(self) -> str:
        return self.data['plugins_dir']

    def get_sections(self, route: List[str] = None) -> Iterator[Section]:
        route = route or []

        sections = [Section(s) for s in self.data['structure']]

        for part in route:
            for section in sections:
                if part == section.name and section.has_subsections():
                    sections = [Section(s) for s in section.subsections]
                    break

        for section in sections:
            yield section

    def get_all_sections(self, route: List[str] = None) -> Iterator[Section]:
        route = route or []

        for section in self.get_sections(route):
            yield section

            if section.has_subsections():
                route.append(section.name)
                yield from self.get_all_sections(route)
                route.pop()

    def _create_folder_structure(self, route: List[str] = None):
        route = route or []

        for section in self.get_sections(route):
            if section.has_subsections():
                self._create_folder(route + [section.name])

                route.append(section.name)
                self._create_folder_structure(route)
                route.pop()
            else:
                self._create_file(route + [section.name])

    def _create_folder(self, route: List[str]):
        folder_path = self.root_folder + "/".join(route)

        if not os.path.isdir(folder_path):
            print("> Create directory", folder_path)
            os.makedirs(folder_path)

    def _create_file(self, route: List[str]):
        file_path = self.root_folder + "/".join(route) + ".json"

        if not os.path.exists(file_path):
            print("> Create file", file_path)
            Computers.create(file_path)
