"""
Test for BotHandler
"""
import unittest
from unittest.mock import Mock
from bot import BotHandler


class TestBotHandler(unittest.TestCase):
    """
    Unit tests for BotHandler
    """

    def setUp(self):
        self.help_menu = (
            "Let me help you:\n"
            "/start\n"
            "/hi\n"
            "/mpoll,<question>,<answer1>,<answers2>,...\n"
            "/poll,<question>,<answer1>,<answers2>,...\n"
            "/search,<search>"
        )

    def test_get_answer(self):
        """
        Test generate answer
        """
        mock_token = Mock()
        bot_handler = BotHandler(mock_token)

        expected_answer_hi = {"action": "message", "message": "Hello, You"}
        expected_answer_help = {"action": "message", "message": self.help_menu}
        expected_answer_mpoll = {
            "action": "send_mpoll",
            "poll": "Test",
            "args": ["foo1", "foo2"],
        }
        expected_answer_poll = {
            "action": "send_poll",
            "poll": "Test",
            "args": ["foo1", "foo2"],
        }
        expected_answer_search = {"action": "search", "search": "search text"}

        self.assertEqual(bot_handler.get_answer("/hi"), expected_answer_hi)
        self.assertEqual(bot_handler.get_answer("/?"), expected_answer_help)
        self.assertEqual(
            bot_handler.get_answer("/mpoll,Test,foo1,foo2"), expected_answer_mpoll
        )
        self.assertEqual(
            bot_handler.get_answer("/poll,Test,foo1,foo2"), expected_answer_poll
        )
        self.assertEqual(
            bot_handler.get_answer("/search,search text"), expected_answer_search
        )
