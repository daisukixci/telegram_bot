# Telegram bot

A bot to do differents things in a group conversation on Telegram.


## Interaction possibles
  * /start: Start to interact with the bot
  * /hi: the bot will say hi :D.
  * /?: Get more information about bot actions.
  * /mpoll, question, answer1, answer2,... : Create a poll with your question and the different answers. Multiple answers allowed.
  * /poll, question, answer1, answer2,... : Create a poll with your question and the different answers.
  * /search, search_text : Search for search_text in all configured search engines.

## Task Scheduler
You can add scheduled task in config.yaml, it works with the same syntax as crontab. Right now, we support action type:
  * message: Send a message to a certain time
Here one example
```yaml
# Every day at 10 AM - say hello in the chat
scheduled_tasks:
    - say_good_morning:
        month: "*"
        day: "*"
        weekday: "*"
        hour: "10"
        minute: "0"
        type: message
        message: "Hello everyone! Have a nice day."
```

## Search configuration
In config.yaml, you can add one Dokuwiki url to use it as search engine. You need to activate XML-RPC API on your instance.
You also need to provide _DOKUWIKI_USER_ and _DOKUWIKI_PASSWORD_ as environement variable or Docker secret.
```
dokuwiki: "https://wiki.tuxtrooper.com"
```

## Contribute
## Poetry
## Tests
### Roadmap
* [ ] Search on wiki,google, whatever
  * [x] Dokuwiki
  * [ ] Search engines
* [ ] Display infra status
* [ ] Organize a party
* [ ] Minigames
* [ ] Reminders
* [ ] Giphy
* [ ] Add installation/usage documentation
