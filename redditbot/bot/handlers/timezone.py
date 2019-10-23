from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext.dispatcher import run_async


LOCATION_MARKUP = ReplyKeyboardMarkup(
    [[KeyboardButton(text="📍 Send location to set timezone", request_location=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


@run_async
def timezone_handler(update, context):
    """Send keyboard with send location button

    Args:
        update (telegram.Update): Object represents an incoming update.
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    text = f"Please, send your location to set your timezone..."
    update.effective_message.reply_html(text, reply_markup=LOCATION_MARKUP)


@run_async
def set_timezone(update, context):
    """Set timezone from location

    Args:
        update (telegram.Update): Object represents an incoming update.
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    message = update.effective_message
    if context.bot.tz_api:
        data = context.bot.tz_api.get_timezone(
            message.location.latitude, message.location.longitude
        )
        if data['status'] == "OK":
            text = f"Your timezone is {data['timeZoneId']} ({data['timeZoneName']})"
            context.bot.db.set_timezone(update.effective_user, data['rawOffset'])
        else:
            text = f"Error response from api: <code>{data['status']}: {data['errorMessage']}</code>"

    else:
        text = "Sorry, administrator disabled this function"
    message.reply_html(text)
