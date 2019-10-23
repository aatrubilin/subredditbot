import os
import typing
import logging
from contextlib import contextmanager

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import as_declarative

logger = logging.getLogger(__name__)

db_url = os.environ.get("DB_URL", "sqlite:///db.sqlite")

engine = sa.create_engine(db_url)
metadata = sa.MetaData(bind=engine)

Session = scoped_session(sessionmaker(bind=engine))


@as_declarative(metadata=metadata)
class Base:
    """Declarative base"""
    
    @classmethod
    def query(cls):
        current_session = Session()
        return current_session.query(cls)

    def add(self):
        current_session = Session()
        current_session.add(self)
        current_session.flush()

    def delete(self):
        current_session = Session()
        current_session.delete(self)
        current_session.flush()

    @staticmethod
    def update():
        current_session = Session()
        current_session.flush()


@contextmanager
def session(**kwargs) -> typing.ContextManager[Session]:
    """Provide a transactional scope around a series of operations."""
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        logger.exception("session commit error, rolling back...")
        new_session.rollback()
        raise
    finally:
        new_session.close()
