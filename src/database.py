"""
DATABASE SETUP FILE
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

_ENGINE = None
_SessionLocal = None


class Base(DeclarativeBase):
    """Declarative base"""

    pass


def get_engine():
    global _ENGINE
    if _ENGINE is None:
        URL = "mysql+pymysql://mongouhd_evernorth:U*dgQkKRuEHe@cp-15.webhostbox.net/mongouhd_evernorth?charset=utf8mb4"
        _ENGINE = create_engine(URL, echo=True)
    return _ENGINE


def get_sessionlocal():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal


def get_db():
    db = get_sessionlocal()()
    try:
        yield db
    finally:
        db.close()
