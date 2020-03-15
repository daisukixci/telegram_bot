#!/usr/bin/env python3

import time
import argparse
import os
import json
import requests
from requests.compat import urljoin


class BotHandler(object):
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
        params = {"timeout": timeout, "offset": offset}
        raw_resp = requests.get(urljoin(self.api_url, "getUpdates"), params)
        try:
            resp = raw_resp.json()
        except json.decoder.JSONDecodeError as error:
            print("Failed to parse response {}: {}.".format(raw_resp.content, error))
            return []

        if "result" not in resp:
            return []
        return resp["result"]

    def send_message(self, chat_id, text):
        params = {"chat_id": chat_id, "text": text}
        return requests.post(urljoin(self.api_url, "sendMessage"), params)

    def send_poll(self, chat_id, question_poll, answer=[]):
        """
        This function allow you to create a poll.
        You can create your question with different answers.
        If you do not specify any answers, "Yes" or "Not" will be set
        by default.
        """

        if len(answer) <= 1:
            answer = ["Yes", "No"]

        params = {"chat_id": chat_id,
                  "question": question_poll,
                  "options": json.dumps(answer),
                  "is_anonymous": False}
        return requests.post(urljoin(self.api_url, "sendPoll"), params)

    def get_answer(self, question):
        if question == "/start":
            return "Hi, I am Exia. How can I help you?\nUse /? to get more information"
        elif question == "/?":
            help_menu = "Let me help you:\n"\
                        "/start\n"\
                        "/Hi\n"\
                        "/newpoll,<question>,<answer1>,<answers2>,...\n"
            return help_menu
        else:
            return self.dialogue_manager.generate_answer(question)


def is_unicode(text):
    return len(text) == len(text.encode())


class SimpleDialogueManager(object):
    """
    This is a simple dialogue manager to test the telegram bot.
    The main part of our bot will be written here.
    """

    def generate_answer(self, question):
        if "Hi" in question:
            return "Hello, You"
        elif question[:8] == "/newpoll":
            question_poll = question.split(",")
            if len(question_poll) >= 2:
                return "send_poll"
            else:
                return "Badger! RTFM"
        else:
            return "Don't be rude. Say Hi first."




def main():
    # Put your own Telegram Access token here...
    token = os.environ["TELEGRAM_API_KEY"]
    simple_manager = SimpleDialogueManager()
    bot = BotHandler(token, simple_manager)
    ###############################################################

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
                        answer = bot.get_answer(update["message"]["text"])
                        if answer == "send_poll":
                            question_poll = text.split(",")
                            answer_poll = question_poll[2:]
                            print(answer_poll)
                            bot.send_poll(chat_id, question_poll[1], answer_poll)
                        else:
                            bot.send_message(chat_id, answer)

                    else:
                        bot.send_message(
                            chat_id,
                            "Hmm, you are sending some weird characters to me...",
                        )
            offset = max(offset, update["update_id"] + 1)
        time.sleep(1)


if __name__ == "__main__":
    main()
