import logging
from datetime import datetime

from db import get_cur_subreddits
from bot.handlers.utils import build_message, get_subreddit_link

logger = logging.getLogger(__name__)


def send_news(context):
    """Send news to subscribers

    Args:
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    time_now = datetime.utcnow().replace(second=0, microsecond=0).time()
    offset = context.bot.news_time - (time_now.hour * 60 + time_now.minute)
    logger.info(f"Send news for users with offset: {offset}")
    for subreddit in get_cur_subreddits():
        data = context.bot.reddit.get_subreddit_top_posts(subreddit.title, limit=5)
        for user in subreddit.users:
            logger.debug(f'User {user} offset: {user.utc_offset_min}')
            if user.utc_offset_min == offset:
                message = f"Subreddit: {get_subreddit_link(subreddit.title)}\n"
                message += build_message(data)

                context.bot.send_message(
                    user.id,
                    message.format(user=user),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )


def backup_db(context):
    """Send backup to admin user

    Args:
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    logger.info("Run backup database")
    if context.bot.admin:
        with context.bot.db.create_dump() as dump_file:
            caption = "\n".join(
                f"<b>{tablename}</b>: {len(data)} rows"
                for tablename, data in dump_file.data.items()
            )
            context.bot.send_document(context.bot.admin, dump_file, caption=caption, parse_mode='HTML')
