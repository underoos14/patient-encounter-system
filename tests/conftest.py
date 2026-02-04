import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.database import Base
print("Test file: ", id(Base))

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """
    Pure SQLAlchemy unit-test session.
    Never touches FastAPI or MySQL.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def block_mysql():
    import src.database

    assert src.database._ENGINE is None


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
