import os
from typing import Iterator, List, Union

from .base_json import BaseJson
from .computers_json import Computers


class Section:
    def __init__(self, section_data: Union[str, dict, None] = None):
        self.name = "N/A"
        self.sections = []
        self.allowed_users = []

        # Initialiize Section from a string
        if isinstance(section_data, str):
            self.name = section_data

        # Initialize Section from a dict
        if isinstance(section_data, dict):
            for key in section_data:
                try:
                    getattr(self, key)
                    setattr(self, key, section_data[key])
                except AttributeError:
                    pass

    @property
    def subsections(self):
        """'sections' and 'subsections' are aliases."""

        return self.sections

    def has_subsections(self):
        """Test if the current section has or not subsections."""

        return bool(self.sections)

    def len(self):
        """Get the number of subsections (TODO: Change to __len__ ??)."""

        return len(self.sections)

    def __str__(self):
        return f"{self.name}: {self.sections}"


class Config(BaseJson):
    def __init__(self, filepath: str):
        """Load the .json from an existent file. Throws if couldn't open/read
        the file."""

        super().__init__(filepath)

        self.root_folder = os.path.dirname(filepath) + "/"
        self.__create_folder_structure()

    @property
    def token(self) -> str:
        """Get the bot's Telegram token."""

        return self.data["token"]

    @property
    def bot_name(self) -> str:
        """Get the bot name."""

        return self.data["name"]

    @property
    def email(self) -> str:
        """Get the email specified on the config.json."""

        return self.data["email"]

    @property
    def server_tmp_dir(self) -> str:
        """
        Get the server's tmp dir, used for storing files downloaded (like plugins
        dropped on the chat for execution)
        """

        return self.data["server_tmp_dir"]

    @property
    def bridge_tmp_dir(self) -> str:
        """
        Get the bridge's tmp dir. In this directory will be stored all the files sent to
        a bridge computer (like plugins for execution).
        """

        return self.data["bridge_tmp_dir"]

    @property
    def remote_tmp_dir(self) -> str:
        """
        Get the remote's tmp dir. In this directory will be stored all the files sent to
        a remote computer (like plugins for execution).
        """

        return self.data["remote_tmp_dir"]

    @property
    def log_dir(self) -> str:
        """Get the directory where to store all the generated logs."""

        return self.data["log_dir"]

    @property
    def plugins_dir(self) -> str:
        """Get the directory where all the plugins are stored."""

        return self.data["plugins_dir"]

    @property
    def check_status_interval(self) -> str:
        """Get the interval of time (in seconds) between each check of the network
        status (Connected computers)"""

        return self.data["check_status_interval"]

    @property
    def admins(self) -> List[str]:
        """Return a list with all the users defined as admin on the config.json"""

        return self.data["admins"]

    def get_section(self, route: List[str] = None) -> Section:
        """
        Return the Section object corresponding to the passed route.
        """

        parent_route = route[:-1]
        section_name = route[-1]

        for section in self.get_sections(parent_route):
            if section_name == section.name:
                return section

        return None

    def get_sections(self, route: List[str] = None) -> Iterator[Section]:
        """
        Return an Iterator with the next direct childs (subsections) from a route, as
        Section objects.

        Example:
            For a structure like
                    Root
                    /  \
                   A1  A2
                   / \
                  B1 B2

            The function would return from the Root: [Section(A1), Section(A2)]
            And, from A1 would return: [Section(B1), Section(B2)]
        """

        route = route or []

        sections = [Section(s) for s in self.data["structure"]]

        for part in route:
            for section in sections:
                if part == section.name and section.has_subsections():
                    sections = [Section(s) for s in section.subsections]
                    break

        for section in sections:
            yield section

    def get_all_sections(self, route: List[str] = None) -> Iterator[Section]:
        """
        Return an Iterator with the all subsections from a route, including the child
        subsections.

        Note:
            The resulting Sections will be ordered like in a depth-first search.

        Example:
            For a structure like
                    Root
                    /  \
                   A1  A2
                   / \
                  B1 B2

            The function would return from the Root:
                [Section(A1), Section(B1), Section(B2), Section(A2)]

            And, from A1 would return: [Section(B1), Section(B2)]
        """

        route = route or []

        for section in self.get_sections(route):
            yield section

            if section.has_subsections():
                route.append(section.name)
                yield from self.get_all_sections(route)
                route.pop()

    def __create_folder_structure(self, route: List[str] = None):
        """
        Create the structur of folders/subfolders and .json files, following the
        config.json structure.
        """

        route = route or []

        for section in self.get_sections(route):
            if section.has_subsections():
                self.__create_folder(route + [section.name])

                route.append(section.name)
                self.__create_folder_structure(route)
                route.pop()
            else:
                self.__create_file(route + [section.name])

    def __create_folder(self, route: List[str]):
        """Create a folder on the specified route if doesn't exists."""

        folder_path = self.root_folder + "/".join(route)

        if not os.path.isdir(folder_path):
            print("> Create directory", folder_path)
            os.makedirs(folder_path)

    def __create_file(self, route: List[str]) -> str:
        """Create a .json file on the specified route if doesn't exists."""

        file_path = self.root_folder + "/".join(route) + ".json"

        if not os.path.exists(file_path):
            print("> Create file", file_path)
            Computers.create(file_path)

        return file_path
