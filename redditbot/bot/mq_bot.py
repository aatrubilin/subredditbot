import logging

import telegram
import telegram.error as tg_error
from telegram.ext import messagequeue as mq
from telegram.ext.dispatcher import run_async

logger = logging.getLogger(__name__)


class MQBot(telegram.bot.Bot):
    """A subclass of Bot which delegates send method handling to MQ"""

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    # noinspection PyBroadException
    def __del__(self):
        try:
            self._msg_queue.stop()
            del self._msg_queue
        except:
            pass

    def delete_user(self, chat_id):
        logger.info(f"Deleting user: {chat_id}")
        if hasattr(self, 'db'):
            with self.db.session():
                user = self.db.User.get(chat_id)
                if user:
                    user.delete()
                else:
                    logger.warning(f"Not found user {chat_id} to delete")

    @run_async
    def _send_message(self, *args, **kwargs):
        try:
            chat_id = args[0]
        except IndexError:
            chat_id = kwargs.get("chat_id")

        try:
            return super(MQBot, self).send_message(*args, **kwargs)
        except tg_error.Unauthorized:
            logger.warning(f"Delete unauthorized user: {chat_id}")
            self.delete_user(chat_id)
        except tg_error.BadRequest as err:
            if err.message == "Chat not found":
                logger.warning(f"Delete not exist user: {chat_id}")
                self.delete_user(chat_id)
            elif "Can't parse entities" in err.message:
                return super(MQBot, self).send_message(
                    chat_id,
                    f"<b>Error sending message</b>\n <code>{err.message}</code>",
                    parse_mode="HTML",
                )
            else:
                logger.exception("send_message BadRequest")
        except:
            logger.exception("Unhandled exception")

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        self._send_message(*args, **kwargs)
