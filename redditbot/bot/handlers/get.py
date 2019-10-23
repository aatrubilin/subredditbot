from telegram.ext.dispatcher import run_async

from .utils import build_message, get_subreddit_from_context, get_subreddit_link


def _get_subreddit_message(context):
    """Get message for selected subreddit from context

    Args:
        context (telegram.ext.CallbackContext): Telegram bot context

    Returns:
        str: Message to send
    """
    subreddit = get_subreddit_from_context(context)
    data = context.bot.reddit.get_subreddit_top_posts(subreddit.text)
    posts_message = build_message(data)
    if posts_message:
        message = f"Subreddit: {subreddit.link}\n"
        message += posts_message
    else:
        message = f"No posts found for subreddit {subreddit.link}"

    return message


def _get_all_messages(context, user):
    """

    Args:
        context (telegram.ext.CallbackContext): Telegram bot context
        user (telegram.User): Telegram user instance

    Yields:
        str: Message to send
    """
    for subreddit in context.bot.db.get_user_subreddit(user.id):
        data = context.bot.reddit.get_subreddit_top_posts(subreddit.title, limit=5)
        message = f"Subreddit: {get_subreddit_link(subreddit.title)}\n"
        message += build_message(data)
        yield message


@run_async
def get_handler(update, context):
    """Get command handler

    Commands:
        /get - Get all subscriptions data
        /get <subreddit> - Get selected subreddit data

    Args:
        update (telegram.Update): Object represents an incoming update.
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    if context.args:
        text = _get_subreddit_message(context)
        update.effective_message.reply_html(text, disable_web_page_preview=True)
    else:
        replied = False
        for text in _get_all_messages(context, update.effective_user):
            replied = True
            update.effective_message.reply_html(text, disable_web_page_preview=True)

        if not replied:
            text = "You have no subscriptions"
            update.effective_message.reply_html(text, disable_web_page_preview=True)
