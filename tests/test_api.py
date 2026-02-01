import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime, timezone
from patient_encounter_systemm.main import app
from patient_encounter_systemm.schemas import schemas


@pytest.fixture
def client():
    """Fixture for creating TestClient."""
    return TestClient(app)


# Mock CRUD operations
@pytest.fixture
def mock_create_patient(mocker):
    return mocker.patch(
        "patient_encounter_systemm.services.crud.create_patient",
        return_value=schemas.PatientCreate(
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            phone="1234567890",
        ),
    )


@pytest.fixture
def mock_get_patient_by_id(mocker):
    return mocker.patch(
        "patient_encounter_systemm.services.crud.get_patient_by_id",
        return_value=schemas.PatientRead(
            pat_id=1,
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            phone="1234567890",
            created_at=datetime(2023, 2, 2, 12, 0, 0, tzinfo=timezone.utc),
            updated_on=datetime(2023, 2, 2, 12, 0, 0, tzinfo=timezone.utc),
        ),
    )


@pytest.fixture
def mock_create_doctor(mocker):
    return mocker.patch(
        "patient_encounter_systemm.services.crud.create_doctor",
        return_value=schemas.DoctorCreate(
            name="Dr. Smith", specialty="Cardiology", reason="Consultation", active=True
        ),
    )


@pytest.fixture
def mock_get_doctor_by_id(mocker):
    return mocker.patch(
        "patient_encounter_systemm.services.crud.get_doctor_by_id",
        return_value=schemas.DoctorRead(
            doc_id=1,
            name="Dr. Smith",
            specialty="Cardiology",
            active=True,
            created_at=datetime(2023, 2, 2, 12, 0, 0, tzinfo=timezone.utc),
        ),
    )


@pytest.fixture
def mock_get_appointments(mocker):
    return mocker.patch(
        "patient_encounter_systemm.services.crud.get_appointment_with_date",
        return_value=[
            schemas.AppointmentRead(
                apt_id=1,
                patient_id=1,
                doctor_id=1,
                reason="Check-up",
                apt_start=datetime(2023, 2, 2, 12, 0, 0, tzinfo=timezone.utc),
                duration=30,
                apt_created_at=datetime(2023, 2, 2, 12, 0, 0, tzinfo=timezone.utc),
            )
        ],
    )


# Test cases
def test_create_patient(client, mock_create_patient):
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone": "1234567890",
    }
    response = client.post("/patients", json=payload)
    assert response.status_code == 201
    assert response.json() == {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone": "1234567890",
    }


def test_get_patient(client, mock_get_patient_by_id):
    response = client.get("/patients/1")
    assert response.status_code == 200
    assert response.json() == {
        "pat_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone": "1234567890",
        "created_at": "2023-02-02T12:00:00Z",  # Changed to 'Z' for UTC
        "updated_on": "2023-02-02T12:00:00Z",  # Changed to 'Z' for UTC
    }


def test_create_doctor(client, mock_create_doctor):
    payload = {
        "name": "Dr. Smith",
        "specialty": "Cardiology",
        "reason": "Consultation",
        "active": True,
    }
    response = client.post("/doctors", json=payload)
    assert response.status_code == 201
    assert response.json() == {
        "name": "Dr. Smith",
        "specialty": "Cardiology",
        "reason": "Consultation",
        "active": True,
    }


def test_get_doctor(client, mock_get_doctor_by_id):
    response = client.get("/doctors/1")
    assert response.status_code == 200
    assert response.json() == {
        "doc_id": 1,
        "name": "Dr. Smith",
        "specialty": "Cardiology",
        "active": True,
        "created_at": "2023-02-02T12:00:00Z",  # Changed to 'Z' for UTC
    }


def test_get_appointments(client, mock_get_appointments):
    response = client.get("/appointments?apt_date=2023-02-02")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0] == {
        "apt_id": 1,
        "patient_id": 1,
        "doctor_id": 1,
        "reason": "Check-up",
        "apt_start": "2023-02-02T12:00:00Z",  # Changed to 'Z' for UTC
        "duration": 30,
        "apt_created_at": "2023-02-02T12:00:00Z",  # Changed to 'Z' for UTC
    }


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}
