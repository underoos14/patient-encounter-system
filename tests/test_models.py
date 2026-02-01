from sqlalchemy import select
from patient_encounter_systemm.models.models import Patient, Doctor, Appointment
from datetime import datetime, timezone
import pytest


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


def test_appointment_invalid_duration(db_session):
    patient = Patient(first_name="Ramesh", last_name="Kumar", email="rameshkumar@gmail.com", phone="9876543210")
    doctor = Doctor(name="Dr. Anjali Rao", specialty="Cardiology", active_status=True)

    appointment = Appointment(
        reason="Test",
        patient=patient,
        doctor=doctor,
        apt_start=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
        apt_duration=-10,
    )

    db_session.add(appointment)
    with pytest.raises(Exception):
        db_session.commit()
