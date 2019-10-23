from telegram.ext.dispatcher import run_async
from .utils import get_subreddit_from_context, get_subreddit_link


def _get_all_subscriptions(context, user):
    """Get all user subscriptions

    Args:
        context (telegram.ext.CallbackContext): Telegram bot context
        user (telegram.User): Telegram user

    Returns:
        str: Result message
    """
    text = ""
    user_subreddits = context.bot.db.get_user_subreddit(user.id)
    for idx, subreddit in enumerate(user_subreddits, 1):
        if not text:
            text += "Your subscriptions:\n"
        else:
            text += "\n"
        text += f"<b>{idx}.</b> {get_subreddit_link(subreddit.title)}"

    if not text:
        text = (
            "You have no subscriptions yet\n"
            "<code>/r python</code> - to subscribe <i>python</i> subreddit"
        )
    return text


def _subscribe(context, user):
    """Subscribe

    Args:
        context (telegram.ext.CallbackContext): Telegram bot context
        user (telegram.User): Telegram user

    Returns:
        str: Result message
    """
    subreddit = get_subreddit_from_context(context)
    subscription = context.bot.db.Subscription.get(user.id, subreddit.text)
    if subscription is None:
        if context.bot.reddit.is_subreddit_has_posts(subreddit.text):
            context.bot.db.subscribe(user, subreddit.text)
            text = f"Subscription to {subreddit.html} success"
        else:
            text = f"No posts found for subreddit {subreddit.html}"
    else:
        text = f"You already subscribed to {subreddit.html}"

    return text


def _unsubscribe(context, user):
    """Unsubscribe

    Args:
        context (telegram.ext.CallbackContext): Telegram bot context
        user (telegram.User): Telegram user

    Returns:
        str: Result message
    """
    subreddit = get_subreddit_from_context(context)
    subscription = context.bot.db.Subscription.get(user.id, subreddit.text)
    if subscription is None:
        text = f"You are not subscribed to {subreddit.html}"
    else:
        context.bot.db.unsubscribe(user.id, subreddit.text)
        text = f"Successfully unsubscribed from {subreddit.html}"

    return text


@run_async
def r_handler(update, context):
    """Subreddit command handler

    Commands:
        /r - Get all subscriptions
        /r <subreddit> - Subscribe to subreddit
        /r -<subreddit> - Unsubscribe from subreddit

    Args:
        update (telegram.Update): Object represents an incoming update.
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    user = update.effective_user
    if not context.args:
        text = _get_all_subscriptions(context, user)
    else:
        unsubscribe = context.args[0].startswith("-")
        if unsubscribe:
            text = _unsubscribe(context, user)
        else:
            text = _subscribe(context, user)

    update.effective_message.reply_html(text, disable_web_page_preview=True)
