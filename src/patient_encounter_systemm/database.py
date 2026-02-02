"""
DATABASE SETUP FILE
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

URL = "mysql+pymysql://mongouhd_evernorth:U*dgQkKRuEHe@cp-15.webhostbox.net/mongouhd_evernorth?charset=utf8mb4"
engine = create_engine(
    URL,
    echo=True,
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Simpler name class"""

    pass


def get_db():
    """initialize db session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
