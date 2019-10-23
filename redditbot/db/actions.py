import csv
import pickle
import logging
from contextlib import contextmanager

from sqlalchemy.ext import serializer

from .base import session, metadata, Session
from .schema import User, Subreddit, Subscription

logger = logging.getLogger(__name__)
DUMP_FILE_NAME = "db.dump"
DUMP_TABLES = (User, Subreddit, Subscription)


def subscribe(user, subreddit):
    """Subscribe user to subreddit

    Args:
        user (telegram.User): Telegram User object
        subreddit (str): Subreddit
    """
    with session():
        usr = User.get_or_create(user.id, user.first_name, user.last_name)
        subr = Subreddit.get_or_create(subreddit)
        usr.subreddits.append(subr)


def unsubscribe(chat_id, subreddit_title):
    """Unsubscribe user from subreddit

    Args:
        chat_id (int): Telegram user id
        subreddit_title (str): Subreddit
    """
    with session():
        subscription = Subscription.get(chat_id, subreddit_title)
        if subscription:
            subscription.delete()


def get_cur_subreddits():
    """Yields subreddits with subscribers

    Yields:
        db.Subreddit: Subreddits
    """
    with session():
        for subreddit in Subreddit.query():
            if subreddit.users:
                yield subreddit


def get_user_subreddit(chat_id, subreddit_title=None):
    """Get subreddit

    Args:
        chat_id (int): Telegram user id
        subreddit_title (str): Subreddit

    Yields:
        db.Subreddit: Subreddits
    """
    with session():
        user = User.get(chat_id)
        if user:
            for subreddit in user.subreddits:
                if subreddit_title is None or subreddit_title == subreddit.title:
                    yield subreddit


def set_timezone(user, offset_seconds):
    """Set user offset

    Args:
        user (telegram.User):
        offset_seconds (int): Offset seconds
    """
    with session():
        usr = User.get_or_create(user.id, user.first_name, user.last_name)
        usr.utc_offset_min = offset_seconds / 60
        usr.update()


@contextmanager
def create_dump():
    """Creating database dump"""
    with session() as sess:
        db_data = {table.__tablename__: sess.query(table).all() for table in DUMP_TABLES}
        db_dump = {
            tablename: serializer.dumps(data) for tablename, data in db_data.items()
        }

        with open(DUMP_FILE_NAME, "wb+") as dump_file:
            pickle.dump(db_dump, dump_file)
            dump_file.seek(0)
            dump_file.data = db_data
            yield dump_file


def restore_dump(dump_file_bytearray):
    """Restoring database

    Args:
        dump_file_bytearray (bytearray): Database dump bytearray

    Returns:
        Dict: Restored data
    """
    db_dump = pickle.loads(dump_file_bytearray)
    restored = {}
    with session() as sess:
        for tablename, table_data in db_dump.items():
            db_data = serializer.loads(table_data, metadata, Session)
            for item in db_data:
                sess.merge(item)
            restored[tablename] = db_data
    return restored


def export_csv():
    """Exporting database to csv

    Yields:
        TextIOWrapper: File data
    """
    with session() as sess:
        for table in DUMP_TABLES:
            filename = f'{table.__tablename__}.csv'

            with open(filename, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                columns = [column.name for column in table.__mapper__.columns]
                writer.writerow(columns)
                for row in sess.query(table):
                    writer.writerow([getattr(row, column) for column in columns])

            with open(filename, 'rb') as csv_file:
                yield csv_file
