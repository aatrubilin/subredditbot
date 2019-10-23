# subredditbot

Subreddit telegram bot sends top 5 daily posts to you at 07:00

[@redditrbot](tg://resolve?domain=redditrbot) - how it works?

### Bot user commands
`/r` - Get all your subscriptions

`/r python` - Subscribe to _python_ subreddit

`/r -python` - Unsubscribe from _python_ subreddit

`/get` - Send all posts now

`/get python` - Send _python_ posts now

`/timezone` - Send keyboard with send location button (to set user timezone)

### Bot admin commands

`/log` - Get app logs

`/dump` - Get database dump `db.dump`

_To restore dataase - share `db.dump` to bot_

`/export` - Export database in *csv

## Getting Started

These instructions will get you a copy of the project up and 
running on your local machine for development and testing purposes.

All commands have been tested on **CentOS Linux release 7.5.1804**

### Prerequisites

Install docker and git

```bash
yum -y install git
yum -y install docker
systemctl start docker
```

### Installing and running

Clone the repo

```bash
git clone https://github.com/aatrubilin/subredditbot
```

Go to project path

```bash
cd subredditbot
```

### Change env variables in [Dockerfile](Dockerfile)

- `TELEGRAM_TOKEN` (**required** ): Telegram bot [token](https://core.telegram.org/bots/api#authorizing-your-bot)
- `TELEGRAM_PROXY` (**optional** ): Telegram [proxy](https://python-telegram-bot.readthedocs.io/en/stable/telegram.utils.request.html#telegram.utils.request.Request)
- `TELEGRAM_ADMIN_ID` (**optional** ): Telegram admin user id
- `GOOGLE_API_KEY` (**optional** ): Google Time [Zone API key](https://developers.google.com/maps/documentation/timezone/intro)
- `LOGGER_LEVEL` (**optional** ): Python logging [level](https://docs.python.org/3/library/logging.html#logging-levels)
- `DB_URL` (**optional** ): Working database [url](https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls)

```dockerfile
...
ENV TELEGRAM_TOKEN <TELEGRAM_TOKEN>
#ENV TELEGRAM_PROXY <TELEGRAM_PROXY>
#ENV TELEGRAM_ADMIN_ID <ADMIN_ID>
#ENV GOOGLE_API_KEY <GOOGLE_API_KEY>
ENV LOGGER_LEVEL INFO
ENV DB_URL sqlite:///db.sqlite
...
```

### Build and run docker

```bash
docker build -t subreddit .
docker run -v /$(pwd)/redditbot:/redditbot:Z -d subreddit
```

## Authors

* **A.A.Trubilin** - [aatrubilin](https://github.com/aatrubilin)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

