#!/usr/bin/env python3
"""
Test for main.py
"""
import unittest
from main import SimpleDialogueManager


class TestMain(unittest.TestCase):
    """
    Main test class
    """

    def test_generate_answer(self):
        """
        Test generate answer
        """
        dialogue_manager = SimpleDialogueManager()
        self.assertEqual(
            dialogue_manager.generate_answer("/newpoll,Test,foo1,foo2"), "send_poll"
        )


if __name__ == "__main__":
    unittest.main()
