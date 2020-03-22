#!/usr/bin/env python3
"""
A simple bot for Telegram conversation that enables to:
    - Say Hi
"""

import random
import sys
import datetime
import os
import json
import time

import yaml
import requests
import croniter
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

        :param chat_id str: ID of the Telegram chat
        :param text str: Message to send on chan_id
        """
        params = {"chat_id": chat_id, "text": text}
        return requests.post(urljoin(self.api_url, "sendMessage"), params)

    def send_poll(self, chat_id, question_poll, answer=[]):
        """
        This function allow you to create a poll.
        You can create your question with different answers.
        If you do not specify any answers, "Yes" or "Not" will be set
        by default.

        :param chat_id str: ID of the Telegram chat
        :param question_poll str: Question for the poll
        :param answer list: Answers possible for the poll
        """

        if len(answer) <= 1:
            answer = ["Yes", "No"]

        params = {
            "chat_id": chat_id,
            "question": question_poll,
            "options": json.dumps(answer),
            "is_anonymous": False,
        }
        return requests.post(urljoin(self.api_url, "sendPoll"), params)

    def run_scheduled_tasks(self, scheduled_tasks=[]):
        """
        This function triggers scheduled_tasks
        Every task is set manually in self.task_schedule to follow the triggers
        """
        actions = []
        now = datetime.datetime.utcnow()
        now = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
        # If not scheduled_tasks, don't do anything
        print(scheduled_tasks)
        for scheduled_task in scheduled_tasks:
            for task, task_conf in scheduled_task.items():
                print(f"Looking if {task} need to be run")
                next_iter = croniter.croniter(
                    f"{task_conf.get('minute', '*')} {task_conf.get('hour', '*')} {task_conf.get('day', '*')} {task_conf.get('month', '*')} {task_conf.get('weekday', '*')}",
                    now,
                )
                next_iter.get_next()
                next_iter.get_prev()
                if now == datetime.datetime.utcfromtimestamp(next_iter.get_current()):
                    print(f"Scheduled task {task} is triggered")
                    if task_conf.get("type", "") == "message":
                        print(f"Task {task} type is message")
                        actions.append(task_conf.get("message", ""))

        return actions

    def get_answer(self, question):
        """
        Generate the answer according to the question

        :param question str: Command/question in the chat
        """
        if question == "/start":
            return "Hi, I am Exia. How can I help you?\nUse /? to get more information"

        if question == "/?":
            help_menu = (
                "Let me help you:\n"
                "/start\n"
                "/Hi\n"
                "/newpoll,<question>,<answer1>,<answers2>,...\n"
            )

            return help_menu

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

        if question[:8] == "/newpoll":
            # Detect the command for a new poll
            question_poll = question.split(",")
            if len(question_poll) >= 2:
                return "send_poll"

            return "Badger! RTFM"

        return self.random_behavior(question)


def get_docker_secret(name, default=None, getenv=True, secrets_dir="/var/run/secrets"):
    """This function fetches a docker secret
    :param name: the name of the docker secret
    :param default: the default value if no secret found
    :param getenv: if environment variable should be fetched as fallback
    :param secrets_dir: the directory where the secrets are stored
    :returns: docker secret or environment variable depending on params
    """
    name_secret = name.lower()
    name_env = name.upper()

    # initialize value
    value = None

    # try to read from secret file
    try:
        with open(os.path.join(secrets_dir, name_secret), "r") as secret_file:
            value = secret_file.read().strip()
            print(f"{name} have been found in docker secret")
    except IOError:
        # try to read from env if enabled
        if getenv:
            value = os.environ.get(name_env)
            print(f"{name} have been found in env")

    # set default value if no value found
    if value is None:
        value = default
        print(f"{name} haven't been found, use default {default}")

    return value


def load_conf(file_path):
    """
    Load configuration from filepath designed file

    :param file_path str: Configuration file path
    """
    with open(file_path) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as error:
            print("Error loading configuration file %s", error)
            return {}
        # TODO: add configuration checks

    return config


def main():
    """
    Handler
    """
    if not (token := get_docker_secret("TELEGRAM_API_KEY")):
        print("No token available, exiting")
        sys.exit(1)

    simple_manager = SimpleDialogueManager()
    bot = BotHandler(token, simple_manager)
    config = load_conf("config.yaml")

    print("Ready to talk!")
    offset = 0
    chat_id = ""
    while True:
        # Send a message
        if chat_id != "":
            print("Looking for scheduled tasks")
            messages = bot.run_scheduled_tasks(config["scheduled_tasks"])
            for message in messages:
                print("Scheduled tasks found, doing them")
                bot.send_message(chat_id, message)

        # Wait a message and answer
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
