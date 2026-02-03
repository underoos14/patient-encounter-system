from datetime import date
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, get_db
from models import models
from schemas import schemas
from services import crud

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Patient Encounter System")


@app.get("/")
def greet():
    """Home page placeholder"""
    return "This is a patient encounter system"


@app.get("/patients/{patient_id}", response_model=schemas.PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """API Endpoint to get patient details by passing patient id"""
    return crud.get_patient_by_id(db, patient_id)


@app.post("/patients", response_model=schemas.PatientCreate, status_code=201)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    """API Endpoint to create a patient profile in database"""
    return crud.create_patient(db, payload)


@app.get("/doctors/{doctor_id}", response_model=schemas.DoctorRead)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """API endpoint to get doctor information by doctor id"""
    return crud.get_doctor_by_id(db, doctor_id)


@app.post("/doctors", response_model=schemas.DoctorCreate, status_code=201)
def create_doctor(payload: schemas.DoctorCreate, db: Session = Depends(get_db)):
    """API Endpoint to create doctor profile in database"""
    return crud.create_doctor(db, payload)


@app.get("/appointments", response_model=list[schemas.AppointmentRead])
def get_appointments(
    apt_date: date, doctor_id: int | None = None, db: Session = Depends(get_db)
):
    """API endpoint to get appointment for a specific date, optionally with doctor id"""
    return crud.get_appointment_with_date(db=db, apt_date=apt_date, doctor_id=doctor_id)


@app.get("/health")
async def health_check():
    """fastapi health check"""
    return {"status": "UP"}
