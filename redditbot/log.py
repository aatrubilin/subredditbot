import os
import logging
from logging.handlers import RotatingFileHandler

LOG_PATH = os.path.join(os.getcwd(), "redditbot.log")


class DuplicateFilter(logging.Filter):
    """Suppressing multiple messages with same content.

    Tracking last logged record and filter out any
    repeated (similar) records. Output something more rsyslog style.

    Example:
        --- The last message repeated 3 times
    """

    def __init__(self):
        super(DuplicateFilter, self).__init__()
        self._last_log = None
        self._last_log_count = 1

    def filter(self, record):
        """Determine if the specified record is to be logged."""
        record.duplicates = ""
        current_log = (record.module, record.levelno, record.msg, record.args)
        if current_log == self._last_log:
            self._last_log_count += 1
            return False
        else:
            if self._last_log_count > 1:
                record.duplicates = (
                    f"--- The last message repeated {self._last_log_count} times\n"
                )

            self._last_log = current_log
            self._last_log_count = 1
            return True


def init_logger(level):
    """Add custom handler and set logger basic config

    Args:
        level (str): Logger level
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)-8s] %(lineno)-4s <%(name)s@%(funcName)s> - %(message)s",
        datefmt="%H:%M:%S",
    )

    root = logging.getLogger()

    file_handler = RotatingFileHandler(
        LOG_PATH, maxBytes=10 * 1024 ** 2, backupCount=3, mode='w'
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        fmt="%(duplicates)s%(asctime)s [%(levelname)-8s] %(lineno)-4s <%(name)s@%(funcName)s> - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(DuplicateFilter())
    root.addHandler(file_handler)
