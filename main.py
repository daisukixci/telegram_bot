#!/usr/bin/env python3
"""
A simple bot for Telegram conversation that enables to:
    - Say Hi
"""

import time
import os
import requests
from requests.compat import urljoin


class BotHandler:
    """
        BotHandler is a class which implements all back-end of the bot.
        It has three main functions:
            'get_updates' — checks for new messages
            'send_message' – posts new message to user
            'get_answer' — computes the most relevant on a user's question
    """

    def __init__(self, token, dialogue_manager):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.dialogue_manager = dialogue_manager

    def get_updates(self, offset=None, timeout=30):
        """
        Gets update from conversation

        :param offset int:
        :param timeout int: Timeout value for getting conversation
        """
        params = {"timeout": timeout, "offset": offset}
        raw_resp = requests.get(urljoin(self.api_url, "getUpdates"), params)
        try:
            resp = raw_resp.json()
        except ValueError as error:
            print(f"Failed to parse response {raw_resp.content}: {error}.")
            return []

        if "result" not in resp:
            return []
        return resp["result"]

    def send_message(self, chat_id, text):
        """
        Send text into chat with chat_id

        :param chat_id : ID of the Telegram chat
        :param text str: Message to send on chan_id
        """
        params = {"chat_id": chat_id, "text": text}
        return requests.post(urljoin(self.api_url, "sendMessage"), params)

    def get_answer(self, question):
        """
        Generate the answer according to the question
        """
        if question == "/start":
            return "Hi, I am your Exia bot. How can I help you today?"
        return self.dialogue_manager.generate_answer(question)


def is_unicode(text):
    """
    Test if the text is unicode or not by comparing size of encoded and "raw" text
    """
    return len(text) == len(text.encode())


class SimpleDialogueManager:
    """
    This is a simple dialogue manager to test the telegram bot.
    The main part of our bot will be written here.
    """

    def generate_answer(self, question):
        """
        Generate an answer according to the question

        :param question str: Command/question for which generate answer
        """
        if "hi" in question.lower():
            return "Hello, You"
        else:
            return "Don't be rude. Say Hi first."


def main():
    """
    Handler
    """
    # Put your own Telegram Access token here...
    token = os.environ["TELEGRAM_API_KEY"]
    simple_manager = SimpleDialogueManager()
    bot = BotHandler(token, simple_manager)

    print("Ready to talk!")
    offset = 0
    while True:
        updates = bot.get_updates(offset=offset)
        for update in updates:
            print("An update received.")
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                if "text" in update["message"]:
                    text = update["message"]["text"]
                    if is_unicode(text):
                        print("Update content: {}".format(update))
                        bot.send_message(
                            chat_id, bot.get_answer(update["message"]["text"])
                        )
                    else:
                        bot.send_message(
                            chat_id,
                            "Hmm, you are sending some weird characters to me...",
                        )
            offset = max(offset, update["update_id"] + 1)
        time.sleep(1)


if __name__ == "__main__":
    main()
