"""Tests for config loading. Run: python -m unittest discover -s tests -t . (from hooks/gate/)."""

import unittest
from pathlib import Path

from config import DEFAULT_STATE_DIR, Config


class ConfigTests(unittest.TestCase):
    def test_defaults_when_nothing_is_set(self):
        config = Config.from_env({})
        self.assertEqual(config.state_dir, DEFAULT_STATE_DIR)
        self.assertTrue(config.reply_check)

    def test_the_plugin_data_dir_is_used_when_present(self):
        config = Config.from_env({"CLAUDE_PLUGIN_DATA": "/data/p"})
        self.assertEqual(config.state_dir, Path("/data/p") / "state")

    def test_the_explicit_state_dir_wins_over_the_plugin_data_dir(self):
        config = Config.from_env({"ENG_STANDARDS_STATE_DIR": "/s", "CLAUDE_PLUGIN_DATA": "/data/p"})
        self.assertEqual(config.state_dir, Path("/s"))

    def test_the_reply_check_is_on_unless_explicitly_turned_off(self):
        for value in ("1", "", "true", "yes", "anything"):
            self.assertTrue(Config.from_env({"ENG_STANDARDS_REPLY_CHECK": value}).reply_check, value)

    def test_the_reply_check_is_off_for_0_false_off_and_no_in_any_case(self):
        for value in ("0", "false", "FALSE", "off", "Off", "no", "NO"):
            self.assertFalse(Config.from_env({"ENG_STANDARDS_REPLY_CHECK": value}).reply_check, value)


if __name__ == "__main__":
    unittest.main()
