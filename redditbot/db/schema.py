import logging

import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref

from .base import Base, session


logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String, default="Anonymous")
    last_name = sa.Column(sa.String)
    utc_offset_min = sa.Column(sa.Integer, default=0)

    subreddits = relationship("Subreddit", secondary="subscriptions")

    def __init__(self, chat_id, first_name, last_name):
        """User

        Args:
            chat_id (int): Telegram user chat id
            first_name (str): Telegram user first name
            last_name (str): Telegram user last name
        """
        self.id = chat_id
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return f"<User({self.id}, {self.first_name}, {self.last_name})>"

    @classmethod
    def get(cls, chat_id):
        """Returns user data

        Args:
            chat_id (int): Telegram user chat id

        Returns:
            db.User: User data
        """
        return cls.query().filter(cls.id == chat_id).one_or_none()

    @classmethod
    def get_or_create(cls, chat_id, first_name, last_name):
        """Get or create user and return it

        Args:
            chat_id (int): Telegram chat id
            first_name (str): User first name
            last_name (str): User last name

        Returns:
            db.User: User instance
        """
        user = cls.get(chat_id)
        if user is None:
            user = cls(chat_id, first_name, last_name)
            user.add()
            logger.info(f"Created User {user}")
        else:
            logger.debug(f"Existed User {user}")

        return user


class Subreddit(Base):
    __tablename__ = "subreddits"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(255))

    users = relationship("User", secondary="subscriptions")

    def __init__(self, title):
        """Subreddit

        Args:
            title (str): Subreddit title
        """
        self.title = title

    def __repr__(self):
        return f"<User({self.id}, {self.title})>"

    @classmethod
    def get(cls, title):
        """Returns user data

        Args:
            title (str): Subreddit title

        Returns:
            db.Subreddit: Subreddit data
        """
        return cls.query().filter(cls.title == title).one_or_none()

    @classmethod
    def get_or_create(cls, title):
        """Get or create subreddit

        Args:
            title (str): Subreddit name

        Returns:
            db.Subreddit: Subreddit instance
        """
        subreddit = cls.get(title)
        if subreddit is None:
            subreddit = cls(title)
            subreddit.add()
            logger.info(f"Created Subreddit {subreddit}")
        else:
            logger.debug(f"Existed Subreddit {subreddit}")

        return subreddit


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    subreddit_id = sa.Column(sa.Integer, sa.ForeignKey("subreddits.id"))

    user = relationship(
        User, backref=backref("subscriptions", cascade="all, delete-orphan")
    )
    subreddit = relationship(
        Subreddit, backref=backref("subscriptions", cascade="all, delete-orphan")
    )

    def __repr__(self):
        return f"<Subscription({self.id}, {self.user_id}, {self.subreddit_id})>"

    @classmethod
    def get(cls, chat_id, subreddit_title):
        """Subscription

        Args:
            chat_id (int): Telegram chat id
            subreddit_title (str): Subreddit title

        Returns:
            db.Subscription: Subscription instance
        """
        subreddit = Subreddit.get(subreddit_title)
        if subreddit:
            return (
                cls.query()
                .filter(cls.user_id == chat_id, cls.subreddit_id == subreddit.id)
                .one_or_none()
            )


Base.metadata.create_all()
