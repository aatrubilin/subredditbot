from telegram.ext.dispatcher import run_async

from .timezone import LOCATION_MARKUP


@run_async
def start_handler(update, context):
    """Send hello message

    Args:
        update (telegram.Update): Object represents an incoming update.
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    user = update.effective_user
    text = (
        f"Hello {user.first_name}\n"
        f"Ths bot send you <b>top 5 post</b> from subreddits "
        f"you subscribed <b>daily</b> morning <b>at 07:00</b>\n"
        f"Whe need your location to set your timezone\n\n"
        f"Available commands:\n"
        f"<code>/r</code> - Get all your subscriptions\n"
        f"<code>/r python</code> - Subscribe to python subreddit\n"
        f"<code>/r -python</code> - Unsubscribe from python subreddit\n"
        f"<code>/get</code> - Send all posts now\n"
        f"<code>/get python</code> - Send python posts now"
    )
    update.effective_message.reply_html(text, reply_markup=LOCATION_MARKUP)
