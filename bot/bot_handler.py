#!/usr/bin/env python3
"""
Telegram bot that can:
    - get conversation updates
    - send message
    - create poll
    - run scheduled task:
        - send message
"""

import datetime
import json

import croniter
import dokuwiki
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

    def __init__(self, token, dokuwiki_creds=None):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.scheduled_tasks = {}
        self.help_menu = (
            "Let me help you:\n"
            "/start\n"
            "/hi\n"
            "/mpoll,<question>,<answer1>,<answers2>,...\n"
            "/poll,<question>,<answer1>,<answers2>,...\n"
            "/search,<search>"
        )

        if dokuwiki_creds:
            try:
                self.dokuwiki_url = dokuwiki_creds.get("url")
                self.dokuwiki = dokuwiki.DokuWiki(
                    dokuwiki_creds.get("url"),
                    dokuwiki_creds.get("user", ""),
                    dokuwiki_creds.get("password", ""),
                    cookieAuth=True,
                )
            except (dokuwiki.DokuWikiError, Exception) as error:
                print(f"Unable to connect to Dokuwiki with error {error}")

        # Emoji faces have to be encoded in unicode to be display in Telegram chat
        self.emoji = {
            ":grinning:": "\U0001F600",
            ":joy:": "\U0001F602",
            ":rolling_laughing:": "\U0001F923",
            ":wink:": "\U0001F609",
            ":zany_face:": "\U0001F92A",
        }

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

    def send_poll(
        self, chat_id, question_poll, answer, multiple_choices=False
    ):
        """
        This function allow you to create a poll.
        You can create your question with different answers.
        If you do not specify any answers, "Yes" or "Not" will be set
        by default.

        :param chat_id str: ID of the Telegram chat
        :param question_poll str: Question for the poll
        :param multiple_choices boolean: If true, allow multiple answers
        :param answer list: Answers possible for the poll
        """

        if len(answer) <= 1:
            answer = ["Yes", "No"]

        params = {
            "chat_id": chat_id,
            "question": question_poll,
            "options": json.dumps(answer),
            "is_anonymous": False,
            "allows_multiple_answers": multiple_choices,
        }
        return requests.post(urljoin(self.api_url, "sendPoll"), params)

    def run_scheduled_tasks(self, scheduled_tasks):
        """
        This function triggers scheduled_tasks
        Every task is set manually in self.task_schedule to follow the triggers
        """
        actions = []
        now = datetime.datetime.now()
        now = datetime.datetime(
            now.year, now.month, now.day, now.hour, now.minute
        )
        # If not scheduled_tasks, don't do anything
        if not scheduled_tasks:
            return actions

        for scheduled_task in scheduled_tasks:
            for task, task_conf in scheduled_task.items():
                print(f"Looking if {task} need to be run")
                next_iter = croniter.croniter(
                    f"{task_conf.get('minute', '*')} {task_conf.get('hour', '*')} {task_conf.get('day', '*')} {task_conf.get('month', '*')} {task_conf.get('weekday', '*')}",
                    now,
                )
                next_iter.get_next()
                next_iter.get_prev()
                if now == datetime.datetime.fromtimestamp(
                    next_iter.get_current()
                ) and self.scheduled_tasks.get(task, False):
                    print(f"Scheduled task {task} is triggered")
                    self.scheduled_tasks[task] = False
                    if task_conf.get("type", "") == "message":
                        print(f"Task {task} type is message")
                        actions.append(task_conf.get("message", ""))
                elif now != datetime.datetime.fromtimestamp(
                    next_iter.get_current()
                ):
                    print(f"Task {task} activated")
                    self.scheduled_tasks[task] = True

        return actions

    def send_search_result(self, chat_id, search):
        """
        Perform a search accross all search engine declared
        and send the answer to the chat with chat_id

        :param chat_id str: ID of the Telegram chat
        :param search str: Term to search
        """
        if hasattr(self, "dokuwiki"):
            print(f"Looking for {search} into dokuwiki")
            urls = []
            for result in self.dokuwiki.pages.search(search):
                urls.append(f"{self.dokuwiki_url}?id={result.get('id')}")

            if urls:
                answer = "\n".join(urls)
            else:
                answer = "No results, sorry"

        if "answer" not in locals():
            answer = "No search engine available"

        print(f"Search result: {answer}")
        self.send_message(chat_id, "Here the results I found:\n" + answer)

    def get_answer(self, question):
        """
        Generate the answer according to the question

        :param question str: Command/question in the chat
        """
        answer = {}
        if question.lower() == "/start":
            answer = {
                "action": "message",
                "message": "Hi, I am Exia. How can I help you?\nUse /? to get more information",
            }

        if "hi" in question.lower():
            answer = {"action": "message", "message": "Hello, You"}

        if question == "/?":
            answer = {"action": "message", "message": self.help_menu}

        if question[:5].lower() == "/poll":
            poll = question.split(",")
            if len(poll) >= 2:
                answer = {
                    "action": "send_poll",
                    "poll": poll[1],
                    "args": poll[2:],
                }
            else:
                answer = {"action": "message", "message": self.help_menu}

        if question[:7].lower() == "/search":
            search = question.split(",")
            print(search)
            if len(search) >= 2:
                answer = {"action": "search", "search": " ".join(search[1:])}
            else:
                answer = {"action": "message", "message": self.help_menu}

        if question[:6].lower() == "/mpoll":
            poll = question.split(",")
            if len(poll) >= 2:
                answer = {
                    "action": "send_mpoll",
                    "poll": poll[1],
                    "args": poll[2:],
                }
            else:
                answer = {"action": "message", "message": self.help_menu}

        return answer
