import unittest

from cmsysbot.utils import Computers


class TestComputers(unittest.TestCase):
    def setUp(self):
        self.computers = Computers("tests/res/computers.json")

    def test_get_names(self):
        computer_names = ["PC1", "PC2", "PC3", "PC4"]

        assert list(self.computers.get_names()) == computer_names
