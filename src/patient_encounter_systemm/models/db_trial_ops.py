from models import Patient, Doctor, Appointment
from sqlalchemy.orm import Session
from sqlalchemy import select, inspect, Table, MetaData
from datetime import datetime
from patient_encounter_systemm.database import Base, engine, get_db


def add_sample_data(db: Session):
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
        apt_start=datetime.now(),
        apt_duration=30,
    )

    db.add_all([patient, doctor, appointment])
    db.commit()

    stmt = select(Appointment).join(Appointment.patient).join(Appointment.doctor)
    appointments = db.execute(stmt).scalars().all()

    print("\nAppointments:")
    for appt in appointments:
        print(
            f"Patient: {appt.patient.first_name}, "
            f"Doctor: {appt.doctor.name}, "
            f"Reason: {appt.reason}"
        )


def list_tables(db: Session):
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    print(table_names)


def remove_mytables(db: Session):
    metadata = MetaData()

    mytables = [
        "varun_appointments",
        "varun_patients",
        "varun_doctors",
    ]

    for table_name in mytables:
        table = Table(table_name, metadata, autoload_with=engine)
        print(f"Dropping table {table_name}")
        table.drop(engine, checkfirst=True)


def describe_tables(db: Session, table_name):
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    for c in columns:
        print(f"Column: {c['name']}, Type: {c['type']}")


# db = next(get_db())
# # list_tables(db)
# # remove_mytables(db)
# # list_tables(db)

# add_sample_data(db)
# list_tables(db)
