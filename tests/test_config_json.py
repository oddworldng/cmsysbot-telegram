import unittest
from unittest.mock import patch

from cmsysbot.utils import Computers, Config, Section


class TestSection(unittest.TestCase):
    def test_empty_initialize(self):
        """Should be able to initialize an empty Section with sane defaults"""

        section = Section()

        assert section.name == "N/A"
        assert section.subsections == []
        assert section.allowed_users == []

    def test_str_initialize(self):
        """Should be able to create a new emtpy Section only by with a name"""

        section = Section("new_section")

        assert section.name == "new_section"
        assert section.subsections == []
        assert section.allowed_users == []

    def test_dict_initialize(self):
        """Should be able to initialize a new Section from a Dict (JSON format)"""

        section_dict = {
            "name": "new_section",
            "sections": ["A", "B"],
            "allowed_users": ["u1", "u2"],
        }

        section = Section(section_dict)

        assert section.name == "new_section"
        assert section.subsections == ["A", "B"]
        assert section.allowed_users == ["u1", "u2"]

    def test_dict_initialize_with_missing_keys(self):
        """Should be able to initialize from a Dict with missing keys, autocompleting
        with the default values"""

        # No "sections" and "allowed_users" keys keys
        section_dict = {"name": "new_section"}

        section = Section(section_dict)

        assert section.name == "new_section"
        assert section.subsections == []
        assert section.allowed_users == []

    def test_dict_initialize_with_unexpected_keys(self):
        """Should ignore unexpected keys present on the Dict object"""

        section_dict = {
            "name": "new_section",
            "unexpected": "This keys should be added to the Section object",
        }

        section = Section(section_dict)

        assert not hasattr(section, "unexpected")

    def test_has_subsections(self):
        """Boolean to test if a section has subsections or not"""

        # Sections defined using only the name shouldn't have subsections
        section = Section("new_section")

        assert not section.has_subsections()

        # Now define some subsections
        section = Section({"sections": ["a", "b"]})

        assert section.has_subsections()


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config: Config = Config("tests/res/config.json")

    def test_token(self):
        assert self.config.token == "TH15T0K3N15NTV4L1D"

    def test_bot_name(self):
        assert self.config.bot_name == "CMSysBot"

    def test_email(self):
        assert self.config.email == "test@test.com"

    def test_server_tmp_dir(self):
        assert self.config.server_tmp_dir == "/tmp/"

    def test_bridge_tmp_dir(self):
        assert self.config.bridge_tmp_dir == "/tmp/"

    def test_remote_tmp_dir(self):
        assert self.config.remote_tmp_dir == "/tmp/"

    def test_log_dir(self):
        assert self.config.log_dir == "log/"

    def test_plugins_dir(self):
        assert self.config.plugins_dir == "plugins/"

    def test_admins(self):
        assert self.config.admins == ["aa", "bb"]

    def test_get_section(self):
        """Should be able to return the individual Section object from its route"""

        section = self.config.get_section(["A1", "B1"])

        assert isinstance(section, Section)
        assert section.name == "B1"
        assert section.subsections == ["C1", "C2"]

    def test_get_sections(self):
        # Get subsections from root
        subsections = list(self.config.get_sections())

        assert len(subsections) == 2
        assert list(map(lambda s: s.name, subsections)) == ["A1", "A2"]

        # Get subsections from route "A1/B1"
        subsections = list(self.config.get_sections(["A1", "B1"]))

        assert len(subsections) == 2
        assert list(map(lambda s: s.name, subsections)) == ["C1", "C2"]

    def test_get_all_sections(self):
        # Get subsections from root
        subsections = list(self.config.get_all_sections())

        assert len(subsections) == 5
        # Depth first
        assert list(map(lambda s: s.name, subsections)) == [
            "A1",
            "B1",
            "C1",
            "C2",
            "A2",
        ]

        # Get subsections from route "A1"
        subsections = list(self.config.get_all_sections(["A1"]))

        assert len(subsections) == 3
        # Depth first
        assert list(map(lambda s: s.name, subsections)) == ["B1", "C1", "C2"]

    @patch("os.path.isdir", return_value=False)
    @patch("os.makedirs")
    def test_create_folder(self, _, os_makedirs_mock):
        """Should try to create a folder with a correct route"""
        self.config._Config__create_folder(["A", "B"])

        os_makedirs_mock.assert_called_with("tests/res/A/B")

    @patch("os.path.exists", return_value=True)
    def test_create_file(self, _):
        """Should try to create a file with a correct route"""

        assert self.config._Config__create_file(["A", "B"]) == "tests/res/A/B.json"
