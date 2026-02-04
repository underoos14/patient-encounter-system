# import pytest
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, Session

# from src.database import Base

# print("Test file: ", id(Base))

# TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"


# @pytest.fixture(scope="function")
# def db_session():
#     engine = create_engine(
#         TEST_DATABASE_URL,
#         connect_args={"check_same_thread": False},
#     )

#     Base.metadata.create_all(bind=engine)

#     SessionLocal = sessionmaker(bind=engine)
#     session = SessionLocal()

#     try:
#         yield session
#     finally:
#         session.close()
#         Base.metadata.drop_all(bind=engine)


# @pytest.fixture(scope="session", autouse=True)
# def block_prod_db(mocker):
#     mocker.patch(
#         "src.database.create_engine",
#         side_effect=RuntimeError("❌ Prod database access attempted during tests"),
#     )


# @pytest.fixture
# def disable_sqlite_conflict_check(mocker):
#     """
#     SQLite does not support INTERVAL / DATE_ADD.
#     This fixture bypasses the conflict check query only.
#     """
#     original_execute = Session.execute

#     def patched_execute(self, statement, *args, **kwargs):
#         sql = str(statement).lower()
#         if "interval" in sql or "date_add" in sql:

#             class DummyResult:
#                 def scalars(self):
#                     return self

#                 def first(self):
#                     return None

#             return DummyResult()
#         return original_execute(self, statement, *args, **kwargs)

#     mocker.patch.object(Session, "execute", patched_execute)

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.database import get_db


@pytest.fixture
def mock_db(mocker):
    """
    Fully mocked SQLAlchemy Session.
    """
    db = mocker.Mock(name="Session")

    # explode immediately if anything touches the DB
    db.execute.side_effect = AssertionError("DB access detected")
    db.commit.side_effect = AssertionError("DB access detected")
    db.refresh.side_effect = AssertionError("DB access detected")
    db.add.side_effect = AssertionError("DB access detected")

    return db

@pytest.fixture
def client(mock_db):
    """
    TestClient created ONLY after dependency override is applied.
    """

    def override_get_db():
        yield mock_db

    # 🔑 CRITICAL: override BEFORE TestClient
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
