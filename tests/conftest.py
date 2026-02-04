# import pytest
# from fastapi.testclient import TestClient

# from src.main import app
# from src.database import get_db


# @pytest.fixture
# def mock_db(mocker):
#     """
#     Fully mocked SQLAlchemy Session.
#     """
#     db = mocker.Mock(name="Session")

#     db.execute.side_effect = AssertionError("DB access detected")
#     db.commit.side_effect = AssertionError("DB access detected")
#     db.refresh.side_effect = AssertionError("DB access detected")
#     db.add.side_effect = AssertionError("DB access detected")

#     return db


# @pytest.fixture
# def client(mock_db):
#     """
#     TestClient created ONLY after dependency override is applied.
#     """

#     def override_get_db():
#         yield mock_db

#     app.dependency_overrides[get_db] = override_get_db

#     with TestClient(app) as c:
#         yield c

#     app.dependency_overrides.clear()

import pytest
from fastapi.testclient import TestClient
from unittest import mock
from src.main import app
from src.database import get_db, get_engine


# Fixture to mock the database session for unit tests
@pytest.fixture
def mock_db(mocker):
    """
    Fully mocked SQLAlchemy Session to avoid actual DB access.
    """
    db = mocker.Mock(name="Session")

    # Mock the methods used for database access, these are the ones that will be used during tests
    db.execute.side_effect = AssertionError("DB access detected")
    db.commit.side_effect = AssertionError("DB access detected")
    db.refresh.side_effect = AssertionError("DB access detected")
    db.add.side_effect = AssertionError("DB access detected")

    return db


@pytest.fixture
def mock_engine(mocker):
    """
    Mock the database engine to avoid actual database connections during testing.
    """
    mock_engine = mocker.Mock(name="Engine")
    
    # Mock any methods of the engine that you expect to use in the tests
    mock_engine.connect.return_value = mock.Mock()  # Mock the `connect` method
    
    return mock_engine


@pytest.fixture
def client(mock_db, mock_engine):
    """
    TestClient created ONLY after dependency overrides for DB session and engine are applied.
    """
    # Mock the `get_db` to return the mocked session
    def override_get_db():
        yield mock_db
    
    # Mock the `get_engine` to return the mocked engine
    def override_get_engine():
        return mock_engine
    
    # Override both the get_db and get_engine with the mocked versions
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_engine] = override_get_engine

    # Return the test client
    with TestClient(app) as c:
        yield c

    # Clean up the dependency overrides after the test is completed
    app.dependency_overrides.clear()


# Fixture to mock database engine creation
@pytest.fixture
def mock_engine_and_session(mocker):
    """
    Mock both the engine and session for testing the database operations.
    This will ensure that no real connections are made to the database.
    """
    mock_engine = mocker.Mock(name="Engine")
    mock_session = mocker.Mock(name="Session")

    # Mock the engine's behavior
    mock_engine.connect.return_value = mock.Mock()

    # Mock the session's behavior
    mock_session.query.return_value = mock.Mock()

    return mock_engine, mock_session




