from fastapi import FastAPI, Depends
from patient_encounter_systemm.database import engine, get_db
from patient_encounter_systemm.models import models
from patient_encounter_systemm.schemas import schemas
from patient_encounter_systemm.services import crud
from sqlalchemy.orm import Session
from datetime import date

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Patient Encounter System")


@app.get("/")
def greet():
    return "This is a patient encounter system"


@app.get("/patients/{patient_id}", response_model=schemas.PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    return crud.get_patient_by_id(db, patient_id)


@app.post("/patients", response_model=schemas.PatientCreate, status_code=201)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.create_patient(db, payload)


@app.get("/doctors/{doctor_id}", response_model=schemas.DoctorRead)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    return crud.get_doctor_by_id(db, doctor_id)


@app.post("/doctors", response_model=schemas.DoctorCreate, status_code=201)
def create_doctor(payload: schemas.DoctorCreate, db: Session = Depends(get_db)):
    return crud.create_doctor(db, payload)


@app.get("/appointments", response_model=list[schemas.AppointmentRead])
def get_appointments(
    apt_date: date, doctor_id: int | None = None, db: Session = Depends(get_db)
):
    return crud.get_appointment_with_date(db=db, apt_date=apt_date, doctor_id=doctor_id)


@app.get("/health")
async def health_check():
    return {"status": "UP"}
