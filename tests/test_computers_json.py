import shutil
import tempfile
import unittest
from os import path
from unittest.mock import patch

from cmsysbot.utils import Computer, Computers


class TestComputer(unittest.TestCase):
    def test_empty_initialize(self):

        computer = Computer()

        assert computer.name == "N/A"
        assert computer.ip == "N/A"
        assert computer.mac == "N/A"
        assert computer.included is True

    def test_dict_initialize(self):

        computer_dict = {
            "name": "comp_name",
            "ip": "11.22.33.44",
            "mac": "aa:bb:cc:dd",
            "included": False,
        }

        computer = Computer(computer_dict)

        assert computer.name == "comp_name"
        assert computer.ip == "11.22.33.44"
        assert computer.mac == "aa:bb:cc:dd"
        assert computer.included is False

    def test_computer_to_dict(self):

        computer = Computer()

        computer_dict = computer.asdict()

        assert "name" in computer_dict
        assert "ip" in computer_dict
        assert "mac" in computer_dict
        assert "included" not in computer_dict


class TestComputers(unittest.TestCase):
    def setUp(self):
        self.computers = Computers("tests/res/computers.json")
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("json.dump")
    def test_create(self, json_dump_mock):
        filepath = path.join(self.test_dir, "new_config_file.json")

        expected_computers_config_dict = {
            "computers": [{"name": "N/A", "ip": "N/A", "mac": "N/A"}]
        }

        created_computers_config_dict = Computers.create(filepath)

        json_dump_mock.assert_called_once()

        assert created_computers_config_dict == expected_computers_config_dict

    def test_add(self):
        self.computers.add("my-name", "my-ip", "my-mac")
        assert len(self.computers) == 5

    def test_remove(self):
        self.computers.remove("40:c1:2e:c6:23:03")
        assert len(self.computers) == 3

        self.computers.remove("inexistent_mac")
        assert len(self.computers) == 3

    def test_find(self):
        computer = self.computers.find("b4:2a:3b:ef:a6:a3")

        assert computer.name == "PC3"

        computer = self.computers.find("inexistent_mac")

        assert computer is None

    def test_get_computers(self):
        assert len(self.computers) == 4

        assert list(map(lambda c: c.name, self.computers)) == [
            "PC1",
            "PC2",
            "PC3",
            "PC4",
        ]

    def test_get_included_computers(self):

        # Exclude two of the computers
        for computer in self.computers:
            if computer.name in ["PC1", "PC3"]:
                computer.included = False

        assert list(map(lambda c: c.name, self.computers.get_included())) == [
            "PC2",
            "PC4",
        ]
