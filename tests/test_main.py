#!/usr/bin/env python3
"""
Test for main.py
"""
import os
import unittest
from unittest.mock import mock_open, patch

import yaml

from main import get_docker_secret, load_conf


class TestMain(unittest.TestCase):
    """
    Main test class
    """

    def test_get_docker_secret(self):
        """
        Test get docker secret
        """
        os.environ["FOO"] = "FOO"
        self.assertEqual(get_docker_secret("foo"), "FOO")
        self.assertEqual(get_docker_secret("none"), None)
        self.assertEqual(
            get_docker_secret("none", default="default"), "default"
        )

    def test_load_conf(self):
        """
        Test configuration loading
        """
        mock_config = """{
            "scheduled_tasks": [
                {
                    "say_good_morning": {
                        "month": "*",
                        "day": "*",
                        "weekday": "*",
                        "hour": "10",
                        "minute": "0",
                        "type": "message",
                        "message": "Hello everyone! Have a nice day.",
                    }
                },
                {
                    "take_a_break": {
                        "month": "*",
                        "day": "*",
                        "weekday": "*",
                        "hour": "16",
                        "minute": "0",
                        "type": "message",
                        "message": "Take a break.",
                    }
                },
            ]
        }"""
        with patch("builtins.open", mock_open(read_data=mock_config)):
            self.assertEqual(
                yaml.safe_load(mock_config), load_conf("fake_path")
            )


if __name__ == "__main__":
    unittest.main()
