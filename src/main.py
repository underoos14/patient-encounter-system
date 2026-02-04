from datetime import date
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import get_engine, get_db
from models import models
from schemas import schemas
from services import crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Patient Encounter System",
    lifespan=lifespan,
)


@app.get("/")
def greet():
    """Home page placeholder"""
    return "This is a patient encounter system"


@app.get("/patients/{patient_id}", response_model=schemas.PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """API Endpoint to get patient details by passing patient id"""
    return crud.get_patient_by_id(db, patient_id)


@app.post("/patients", status_code=201)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    """API Endpoint to create a patient profile in database"""
    return crud.create_patient(db, payload)


@app.get("/doctors/{doctor_id}", response_model=schemas.DoctorRead)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """API endpoint to get doctor information by doctor id"""
    return crud.get_doctor_by_id(db, doctor_id)


@app.post("/doctors", status_code=201)
def create_doctor(payload: schemas.DoctorCreate, db: Session = Depends(get_db)):
    """API Endpoint to create doctor profile in database"""
    return crud.create_doctor(db, payload)


@app.get("/appointments", response_model=list[schemas.AppointmentRead])
def get_appointments(
    apt_date: date, doctor_id: int | None = None, db: Session = Depends(get_db)
):
    """API endpoint to get appointment for a specific date, optionally with doctor id"""
    return crud.get_appointment_with_date(db=db, apt_date=apt_date, doctor_id=doctor_id)


@app.post("/appointments", status_code=201)
def create_appointment(
    payload: schemas.AppointmentCreate, db: Session = Depends(get_db)
):
    """API endpoint to create an appointment"""
    return crud.create_appointment(db, payload)


@app.get("/health")
async def health_check():
    """fastapi health check"""
    return {"status": "UP"}
