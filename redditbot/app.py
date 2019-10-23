import os
import logging
from datetime import datetime, time

from telegram.utils.request import Request
from telegram.ext.messagequeue import MessageQueue
from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, MessageHandler

import db
import tasks
from log import init_logger
from reddit import Reddit
from googleapi.timezone import TimeZoneAPI
from bot import MQBot, handlers


if __name__ == "__main__":
    init_logger(os.environ.get("LOGGER_LEVEL", "WARNING"))
    logger = logging.getLogger(__name__)
    logger.info(f'Starting bot...')

    token = os.environ.get("TELEGRAM_TOKEN")
    if token is None:
        raise RuntimeError("Set environ variable TELEGRAM_TOKEN")

    request_kwargs = {"con_pool_size": 8, "connect_timeout": 10, "read_timeout": 3}
    proxy = os.environ.get("TELEGRAM_PROXY")
    if proxy:
        request_kwargs["proxy_url"] = proxy
        logger.info(f"Run with proxy: {proxy}")
    else:
        logger.warning("Running bot without proxy!")

    bot = MQBot(
        token,
        request=Request(**request_kwargs),
        mqueue=MessageQueue(all_burst_limit=29, all_time_limit_ms=1017),
    )

    bot.db = db
    bot.reddit = Reddit()
    bot.admin = int(os.environ.get("TELEGRAM_ADMIN_ID", 0))
    bot.tz_api = None
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if google_api_key:
        bot.tz_api = TimeZoneAPI(google_api_key)

    bot.news_time = time(hour=8, minute=00)
    bot.news_time = bot.news_time .hour * 60 + bot.news_time .minute  # get minutes

    updater = Updater(bot=bot, use_context=True)
    dp = updater.dispatcher
    jobs = updater.job_queue

    dp.add_handler(CommandHandler("start", handlers.start_handler))
    dp.add_handler(CommandHandler("r", handlers.r_handler))
    dp.add_handler(CommandHandler("get", handlers.get_handler))
    dp.add_handler(CommandHandler("timezone", handlers.timezone_handler))
    dp.add_handler(MessageHandler(Filters.location, handlers.set_timezone))

    jobs.run_repeating(tasks.send_news, 60, 0)

    if bot.admin:
        dp.add_handler(
            CommandHandler("log", handlers.admin.log_handler, Filters.chat(bot.admin))
        )
        dp.add_handler(
            CommandHandler("dump", handlers.admin.dump_handler, Filters.chat(bot.admin))
        )
        dp.add_handler(
            CommandHandler("export", handlers.admin.export_handler, Filters.chat(bot.admin))
        )
        dp.add_handler(
            MessageHandler(
                Filters.document & Filters.chat(bot.admin),
                handlers.admin.restore_handler,
            )
        )

        jobs.run_daily(tasks.backup_db, time(hour=17, minute=00))

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
