#!/usr/bin/env python3
"""
Dialogue manager to generate answer for Telegram bot according to received message
"""

import random


class DialogueManager:
    """
    This is a simple dialogue manager to test the telegram bot.
    The main part of our bot will be written here.
    """

    def __init__(self):
        # Emoji faces have to be encoded in unicode to be display in Telegram chat
        self.emoji = {
            ":grinning:": "\U0001F600",
            ":joy:": "\U0001F602",
            ":rolling_laughing:": "\U0001F923",
            ":wink:": "\U0001F609",
            ":zany_face:": "\U0001F92A",
        }

        self.article_opinion = [
            "So cool!",
            "Nice!",
            "Interesting! keep me in touch if you get more details on it",
            "Cool! but I've already read it",
        ]

        self.party_opinion = [
            "I'm in!",
            "Party!",
            "Go! I bring the beers",
            "Let's go for a party",
        ]

        self.random_proposal = [
            "Enjoy your day!",
            "Who is ready for a party?",
            "I'm playing CS guys! join me",
            "How are you guys?",
            "The weather is really bad!",
        ]

    def random_behavior(self, question):
        """
        This function improves the bot conversation in the Telegram chat

        :param question str: Command/question in the chat
        """
        probability = random.randint(1, 100)

        if "exia" in question.lower():
            return "Let me help you: use /?"

        if "http" in question.lower():
            # return an article opinion
            return random.choice(self.article_opinion)

        if "party" in question.lower():
            # return an article opinion
            return random.choice(self.party_opinion)

        if (
            "mdr" in question.lower()
            or "lol" in question.lower()
            or self.emoji[":grinning:"] in question
            or self.emoji[":joy:"] in question
        ):
            # return a happy emojy
            return random.choice(
                [
                    self.emoji[":grinning:"],
                    self.emoji[":joy:"],
                    self.emoji[":rolling_laughing:"],
                ]
            )

        if probability <= 5:
            return random.choice(self.random_proposal)

        return ""

    def generate_answer(self, question):
        """
        Generate an answer according to the question

        :param question str: Command/question for which generate answer
        """
        if "hi" in question.lower():
            return "Hello, You"

        if question[:5] == "/poll":
            # Detect the command for a new poll
            question_poll = question.split(",")
            if len(question_poll) >= 2:
                return "send_poll"
        elif question[:6] == "/mpoll":
            # Detect the command for a new poll
            question_poll = question.split(",")
            if len(question_poll) >= 2:
                return "send_mpoll"

            return "Badger! RTFM"

        return self.random_behavior(question)
