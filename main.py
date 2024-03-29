#!/usr/bin/env python3
"""
A simple bot for Telegram conversation that enables to:
    - Say hi
"""

import os
import sys
import time

import yaml

from bot import BotHandler


def get_docker_secret(
    name, default=None, getenv=True, secrets_dir="/var/run/secrets"
):
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
            if value:
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


def scheduled_tasks(chat_id, bot, config):
    """
    Run the scheduled tasks
    """
    print("Looking for scheduled tasks")
    messages = bot.run_scheduled_tasks(config["scheduled_tasks"])
    for message in messages:
        print("Scheduled tasks found, doing them")
        bot.send_message(chat_id, message)


def main():
    """
    Handler
    """
    if not (token := get_docker_secret("TELEGRAM_API_KEY")):
        print("No token available, exiting")
        sys.exit(1)

    config = load_conf("config.yaml")
    dokuwiki_creds = {
        "url": config["dokuwiki"],
        "user": get_docker_secret("DOKUWIKI_USER"),
        "password": get_docker_secret("DOKUWIKI_PASSWORD"),
    }
    bot = BotHandler(token, dokuwiki_creds)

    print("Ready to talk!")
    offset = 0
    chat_id = ""
    while True:
        # Send a message
        if chat_id != "":
            scheduled_tasks(chat_id, bot, config)

        # Wait a message and answer
        updates = bot.get_updates(offset=offset)
        for update in updates:
            print("An update received.")
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                if "text" in update["message"]:
                    print("Update content: {}".format(update))
                    answer = bot.get_answer(update["message"]["text"])
                    if answer.get("action") == "send_poll":
                        bot.send_poll(
                            chat_id, answer.get("poll"), answer.get("args")
                        )
                    elif answer.get("action") == "send_mpoll":
                        bot.send_poll(
                            chat_id,
                            answer.get("poll"),
                            answer.get("args"),
                            True,
                        )
                    elif answer.get("action") == "search":
                        bot.send_search_result(chat_id, answer.get("search"))
                    else:
                        try:
                            bot.send_message(chat_id, answer.get("message"))
                        except KeyError:
                            print("Message key is missing")

            offset = max(offset, update["update_id"] + 1)
        time.sleep(1)


if __name__ == "__main__":
    main()
