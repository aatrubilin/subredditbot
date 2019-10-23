import os
import logging

from telegram.ext.dispatcher import run_async

from log import LOG_PATH

logger = logging.getLogger(__name__)


@run_async
def log_handler(update, context):
    """Send log

    Args:
        update (telegram.Update): Object represents an incoming update.
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    if os.path.isfile(LOG_PATH):
        update.effective_message.reply_document(open(LOG_PATH, "rb"))
    else:
        update.effective_message.reply_html(f'Log file not found\n<code>{LOG_PATH}</code>')


@run_async
def dump_handler(update, context):
    """Send database dump

    Args:
        update (telegram.Update): Object represents an incoming update.
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    with context.bot.db.create_dump() as dump_file:
        caption = "\n".join(
            f"<b>{tablename}</b>: {len(data)} rows"
            for tablename, data in dump_file.data.items()
        )
        update.effective_message.reply_document(dump_file, caption=caption, parse_mode='HTML')


@run_async
def restore_handler(update, context):
    """Restore database

    Args:
        update (telegram.Update): Object represents an incoming update.
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    message = update.effective_message
    if message.document.file_name == context.bot.db.DUMP_FILE_NAME:
        dump_file = message.document.get_file()
        restore_result = context.bot.db.restore_dump(dump_file.download_as_bytearray())

        restore_result_str = "\n".join(
            f"<b>{tablename}</b>: {len(data)} rows"
            for tablename, data in restore_result.items()
        )
        message.reply_html(f'Successfully restored:\n{restore_result_str}')
    else:
        message.reply_html(f'Bad file name: <b>{message.document.file_name}</b>')


@run_async
def export_handler(update, context):
    """Send exported database in csv format

    Args:
        update (telegram.Update): Object represents an incoming update.
        context (telegram.ext.CallbackContext): Telegram bot context
    """
    for csv_file in context.bot.db.export_csv():
        update.effective_message.reply_document(csv_file)
