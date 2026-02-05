from datetime import datetime, timedelta, timezone, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, select, func
from fastapi import HTTPException
from schemas import schemas
from models import models


def get_patient_by_id(db: Session, patient_id: int) -> models.Patient:
    """database operation to get patient by id"""
    patient = db.get(models.Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


def get_doctor_by_id(db: Session, doctor_id: int) -> models.Doctor:
    """database operation to get doctor by id"""
    doctor = db.get(models.Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


def get_appointment_with_date(
    db: Session, apt_date: date, doctor_id: int | None = None
):
    """database operation to get valid appointment with date and doctor id"""
    start = datetime.combine(apt_date, datetime.min.time(), tzinfo=timezone.utc)
    end = datetime.combine(apt_date, datetime.max.time(), tzinfo=timezone.utc)

    query = select(models.Appointment).where(
        models.Appointment.apt_start.between(start, end)
    )

    if doctor_id:
        query = query.where(models.Appointment.doctor_id == doctor_id)

    return db.execute(query).scalars().all()


def create_patient(db: Session, payload: schemas.PatientCreate) -> models.Patient:
    """database operation to create patient profile"""
    try:
        patient = models.Patient(**payload.model_dump())
        db.add(patient)
        db.commit()
        db.refresh(patient)

        return patient
    except Exception:
        raise HTTPException(status_code=422, detail="wrong patient fields")


def create_doctor(db: Session, payload: schemas.DoctorCreate) -> models.Doctor:
    """database operation to create doctor fields"""
    try:
        doctor = models.Doctor(**payload.model_dump())
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        return doctor
    except Exception:
        raise HTTPException(status_code=422, detail="wrong doctor fields")


def create_appointment(
    db: Session, payload: schemas.AppointmentCreate
) -> models.Appointment:
    """database operation to create valid appointment"""
    start_time = payload.apt_start.astimezone(timezone.utc)
    end_time = start_time + timedelta(minutes=payload.apt_duration)

    if start_time <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400, detail="Appointments must be scheduled at a later time"
        )

    doctor = db.get(models.Doctor, payload.doctor_id)
    if not doctor or not doctor.active_status:
        raise HTTPException(
            status_code=400, detail="Doctor is inactive or doesn't exist"
        )

    overlap_stmt = select(models.Appointment).where(
        and_(
            models.Appointment.doctor_id == payload.doctor_id,
            models.Appointment.apt_start < end_time,
            func.date_add(
                models.Appointment.apt_start,
                func.interval(models.Appointment.apt_duration, "MINUTE"),
            )
            > start_time,
        )
    )
    print(f"Overlap query: {overlap_stmt}")
    overlap = db.execute(overlap_stmt).scalars().first()
    if overlap:
        raise HTTPException(
            status_code=409, detail="Doctor has a conflicting appointment"
        )

    apt = models.Appointment(
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        reason=payload.reason,
        apt_start=start_time,
        apt_duration=payload.apt_duration,
    )

    db.add(apt)
    db.commit()
    db.refresh(apt)
    return apt
