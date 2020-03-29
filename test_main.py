#!/usr/bin/env python3
"""
Test for main.py
"""
import os
import unittest
from main import DialogueManager
from main import get_docker_secret


class TestMain(unittest.TestCase):
    """
    Main test class
    """

    def test_generate_answer(self):
        """
        Test generate answer
        """
        dialogue_manager = DialogueManager()
        self.assertEqual(
            dialogue_manager.generate_answer("/poll,Test,foo1,foo2"), "send_poll"
        )
        self.assertEqual(
            dialogue_manager.generate_answer("/mpoll,Test,foo1,foo2"), "send_mpoll"
        )

    def test_get_docker_secret(self):
        """
        Test get docker secret
        """
        os.environ["FOO"] = "FOO"
        self.assertEqual(get_docker_secret("foo"), "FOO")
        self.assertEqual(get_docker_secret("none"), None)
        self.assertEqual(get_docker_secret("none", default="default"), "default")


if __name__ == "__main__":
    unittest.main()
