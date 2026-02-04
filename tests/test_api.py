import pytest
from datetime import datetime, timezone, timedelta
from src.schemas import schemas


# Mock CRUD operations
@pytest.fixture
def mock_create_patient(mocker):
    return mocker.patch(
        "src.main.crud.create_patient",
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
        "src.main.crud.get_patient_by_id",
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
        "src.main.crud.create_doctor",
        return_value=schemas.DoctorCreate(
            name="Dr. Smith", specialty="Cardiology", reason="Consultation", active=True
        ),
    )


@pytest.fixture
def mock_get_doctor_by_id(mocker):
    return mocker.patch(
        "src.main.crud.get_doctor_by_id",
        return_value=schemas.DoctorRead(
            doc_id=1,
            name="Dr. Smith",
            specialty="Cardiology",
            active=True,
            created_at=datetime(2023, 2, 2, 12, 0, 0, tzinfo=timezone.utc),
        ),
    )


@pytest.fixture
def mock_get_doctor_by_id_inactive(mocker):
    return mocker.patch(
        "src.main.crud.get_doctor_by_id",
        return_value=schemas.DoctorRead(
            doc_id=2,
            name="Dr. Snow",
            specialty="Radiology",
            active=False,
            created_at=datetime(2023, 2, 2, 13, 0, 0, tzinfo=timezone.utc),
        ),
    )


@pytest.fixture
def mock_get_appointments(mocker):
    return mocker.patch(
        "src.main.crud.get_appointment_with_date",
        return_value=[
            schemas.AppointmentRead(
                apt_id=1,
                patient_id=1,
                doctor_id=1,
                reason="Check-up",
                apt_start=datetime(2023, 2, 2, 12, 0, 0, tzinfo=timezone.utc),
                apt_duration=30,
                apt_created_at=datetime(2023, 2, 2, 12, 0, 0, tzinfo=timezone.utc),
            )
        ],
    )


@pytest.fixture
def mock_create_appointment(mocker):
    return mocker.patch(
        "src.main.crud.create_appointment",
        return_value=schemas.AppointmentCreate(
            patient_id=1,
            doctor_id=1,
            reason="Check-up",
            apt_start=datetime(2023, 2, 2, 12, 0, 0, tzinfo=timezone.utc),
            apt_duration=30,
        ),
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
    assert (
        response.json()["first_name"]
        == mock_create_patient.return_value.model_dump()["first_name"]
    )


def test_get_patient(client, mock_get_patient_by_id):
    response = client.get("/patients/1")
    assert response.status_code == 200
    assert (
        response.json()["pat_id"]
        == mock_get_patient_by_id.return_value.model_dump()["pat_id"]
    )


def test_create_doctor(client, mock_create_doctor):
    payload = {
        "name": "Dr. Smith",
        "specialty": "Cardiology",
        "reason": "Consultation",
        "active": True,
    }
    response = client.post("/doctors", json=payload)
    assert response.status_code == 201
    assert (
        response.json()["active"]
        == mock_create_doctor.return_value.model_dump()["active"]
    )


def test_get_doctor(client, mock_get_doctor_by_id):
    response = client.get("/doctors/1")
    assert response.status_code == 200
    assert (
        response.json()["doc_id"]
        == mock_get_doctor_by_id.return_value.model_dump()["doc_id"]
    )


def test_create_appointment(client, mock_create_appointment):
    payload = {
        "patient_id": 1,
        "doctor_id": 1,
        "reason": "Check-up",
        "apt_start": datetime(2023, 2, 2, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
        "apt_duration": 30,
    }
    response = client.post("/appointments", json=payload)
    print(response.json())
    assert response.status_code == 201
    assert (
        response.json()["apt_duration"]
        == mock_create_appointment.return_value.model_dump()["apt_duration"]
    )


def test_create_appointment_in_the_past(client):
    # Simulate the current time as a datetime in the past
    past_time = datetime.now(timezone.utc) - timedelta(days=1)

    payload = {
        "patient_id": 1,
        "doctor_id": 1,
        "reason": "Consultation",
        "apt_start": past_time.isoformat(),  # Using a time in the past
        "apt_duration": 30,
    }

    response = client.post("/appointments", json=payload)
    print(response.json())
    assert response.status_code == 400
    assert response.json()["detail"] == "Appointments must be scheduled at a later time"


def test_create_appointment_invalid_doctor(client, mock_get_doctor_by_id_inactive):
    # Mock that the doctor is inactive or doesn't exist
    payload = {
        "patient_id": 1,
        "doctor_id": 2,  # Non-existent or inactive doctor
        "reason": "Consultation",
        "apt_start": datetime(2026, 3, 2, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
        "apt_duration": 30,
    }

    response = client.post("/appointments", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Doctor is inactive or doesn't exist"


def test_get_appointments(client, mock_get_appointments):
    response = client.get("/appointments?apt_date=2023-02-02")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert (
        response.json()[0]["apt_id"]
        == mock_get_appointments.return_value[0].model_dump()["apt_id"]
    )


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}
