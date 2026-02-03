import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.database import Base

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def disable_sqlite_conflict_check(mocker):
    """
    SQLite does not support INTERVAL / DATE_ADD.
    This fixture bypasses the conflict check query only.
    """
    original_execute = Session.execute

    def patched_execute(self, statement, *args, **kwargs):
        sql = str(statement).lower()
        if "interval" in sql or "date_add" in sql:

            class DummyResult:
                def scalars(self):
                    return self

                def first(self):
                    return None

            return DummyResult()
        return original_execute(self, statement, *args, **kwargs)

    mocker.patch.object(Session, "execute", patched_execute)
