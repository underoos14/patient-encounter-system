from datetime import datetime, timezone, date, timedelta
import pytest
from sqlalchemy import select
from fastapi import HTTPException
from src.models.models import Patient, Doctor, Appointment
from src.services import crud
from src.schemas import schemas


def test_create_patient(db_session):
    patient = Patient(
        first_name="Ramesh",
        last_name="Kumar",
        email="rameshkumar@gmail.com",
        phone="9876543210",
    )
    db_session.add(patient)
    db_session.commit()

    saved_patient = db_session.get(Patient, patient.pat_id)

    assert saved_patient is not None
    assert saved_patient.first_name == "Ramesh"
    assert saved_patient.last_name == "Kumar"
    assert saved_patient.email == "rameshkumar@gmail.com"
    assert saved_patient.phone == "9876543210"


def test_create_doctor(db_session):
    doctor = Doctor(name="Dr. Anjali Rao", specialty="Cardiology", active_status=True)
    db_session.add(doctor)
    db_session.commit()

    saved_doctor = db_session.get(Doctor, doctor.doc_id)

    assert saved_doctor is not None
    assert saved_doctor.name == "Dr. Anjali Rao"
    assert saved_doctor.specialty == "Cardiology"
    assert saved_doctor.active_status is True


def test_create_appointment(db_session):
    patient = Patient(
        first_name="Ramesh",
        last_name="Kumar",
        email="rameshkumar@gmail.com",
        phone="9876543210",
    )
    doctor = Doctor(name="Dr. Anjali Rao", specialty="Cardiology", active_status=True)

    appointment = Appointment(
        reason="Chest pain evaluation",
        patient=patient,
        doctor=doctor,
        apt_start=datetime(2026, 2, 1, 17, 0, tzinfo=timezone.utc),
        apt_duration=30,
    )

    db_session.add(appointment)
    db_session.commit()

    stmt = select(Appointment)
    result = db_session.execute(stmt).scalars().one()

    assert result is not None
    assert result.reason == "Chest pain evaluation"
    assert result.patient.first_name == "Ramesh"
    assert result.doctor.specialty == "Cardiology"
    assert result.apt_duration == 30


def test_get_patient_by_id_success(db_session):
    patient = Patient(
        first_name="Ramesh",
        last_name="Kumar",
        email="ramesh@gmail.com",
        phone="9999999999",
    )
    db_session.add(patient)
    db_session.commit()

    result = crud.get_patient_by_id(db_session, patient.pat_id)

    assert result.pat_id == patient.pat_id
    assert result.first_name == "Ramesh"


def test_get_patient_by_id_not_found(db_session):
    with pytest.raises(HTTPException) as exc:
        crud.get_patient_by_id(db_session, 9999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Patient not found"


def test_get_doctor_by_id_success(db_session):
    doctor = Doctor(
        name="Dr. Anjali Rao",
        specialty="Cardiology",
        active_status=True,
    )
    db_session.add(doctor)
    db_session.commit()

    result = crud.get_doctor_by_id(db_session, doctor.doc_id)

    assert result.doc_id == doctor.doc_id
    assert result.active_status is True


def test_get_doctor_by_id_not_found(db_session):
    with pytest.raises(HTTPException) as exc:
        crud.get_doctor_by_id(db_session, 9999)

    assert exc.value.status_code == 404


def test_get_appointment_with_date_filters_by_day(db_session):
    patient = Patient(
        first_name="Ramesh",
        last_name="Kumar",
        email="r@gmail.com",
        phone="7777777777",
    )
    doctor = Doctor(
        name="Dr. Rao",
        specialty="Cardiology",
        active_status=True,
    )

    apt = Appointment(
        patient=patient,
        doctor=doctor,
        reason="Consultation",
        apt_start=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
        apt_duration=30,
    )

    db_session.add_all([apt])
    db_session.commit()

    result = crud.get_appointment_with_date(
        db_session, date(2026, 2, 1), doctor_id=doctor.doc_id
    )

    assert len(result) == 1
    assert result[0].doctor_id == doctor.doc_id


def test_create_appointment_in_past_fails(db_session):
    payload = schemas.AppointmentCreate(
        patient_id=1,
        doctor_id=1,
        apt_start=datetime.now(timezone.utc) - timedelta(hours=1),
        apt_duration=30,
    )

    with pytest.raises(HTTPException) as exc:
        crud.create_appointment(db_session, payload)

    assert exc.value.status_code == 400


def test_create_appointment_inactive_doctor_fails(db_session):
    patient = Patient(
        first_name="Ramesh",
        last_name="Kumar",
        email="r@gmail.com",
        phone="6666666666",
    )
    doctor = Doctor(
        name="Dr. Inactive",
        specialty="ENT",
        active_status=False,
    )

    db_session.add_all([patient, doctor])
    db_session.commit()

    payload = schemas.AppointmentCreate(
        patient_id=patient.pat_id,
        doctor_id=doctor.doc_id,
        apt_start=datetime.now(timezone.utc) + timedelta(hours=2),
        apt_duration=30,
    )

    with pytest.raises(HTTPException) as exc:
        crud.create_appointment(db_session, payload)

    assert exc.value.status_code == 400


def test_create_appointment_success(db_session, disable_sqlite_conflict_check):
    patient = Patient(
        first_name="Asha",
        last_name="Verma",
        email="asha@gmail.com",
        phone="4444444444",
    )
    doctor = Doctor(
        name="Dr. Mehta",
        specialty="Orthopedics",
        active_status=True,
    )

    db_session.add_all([patient, doctor])
    db_session.commit()

    payload = schemas.AppointmentCreate(
        patient_id=patient.pat_id,
        doctor_id=doctor.doc_id,
        reason="Consultation",
        apt_start=datetime.now(timezone.utc) + timedelta(hours=3),
        apt_duration=45,
    )

    apt = crud.create_appointment(db_session, payload)

    assert apt.apt_id is not None
    assert apt.apt_duration == 45
