import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.db_models import Base

_ENGINE = None
_SESSION_LOCAL = None


def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set")
    return database_url


def init_db():
    global _ENGINE, _SESSION_LOCAL
    if _ENGINE is None:
        _ENGINE = create_engine(_get_database_url(), pool_pre_ping=True)
        _SESSION_LOCAL = sessionmaker(bind=_ENGINE, autocommit=False, autoflush=False)

    Base.metadata.create_all(bind=_ENGINE)
    return _SESSION_LOCAL


def get_session():
    if _SESSION_LOCAL is None:
        init_db()
    return _SESSION_LOCAL()
