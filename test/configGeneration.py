import os
import pickle
import unittest
from unittest.mock import patch
from src.vue.Core import Core
from src.main import verifying_path


class TestDefaultConfig(unittest.TestCase):
    def setUp(self):
        self.core = Core()

    def tearDown(self):
        if os.path.exists("config"):
            os.remove("config")

    def test_default_config_creates_config_file(self):
        self.core.default_config()
        self.assertTrue(os.path.isfile("config"))

    @patch('src.vue.Core.Core.game_version', return_value="0.0.1")
    def test_default_config_writes_correct_data_to_config_file(self, mock_game_version):
        self.core.default_config()
        with open("config", "rb") as configFile:
            config_data = pickle.load(configFile)
        self.assertEqual(config_data["version"], "0.0.1")
        self.assertEqual(config_data["fullscreen"], True)
        self.assertIsInstance(config_data["width"], int)
        self.assertIsInstance(config_data["height"], int)
        self.assertEqual(config_data["volume"], 0.1)


if __name__ == '__main__':
    unittest.main()
