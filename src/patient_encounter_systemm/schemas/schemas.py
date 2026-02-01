from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class ORMBase(BaseModel):
    model_config = {"from_attributes": True}


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phonenum(cls, value):
        digits = re.sub(r"\D", "", value)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Phone number must be between 10 and 15 digits")
        return f"{digits}"

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if "@" not in value:
            raise ValueError("Invalid email address")
        return value


class PatientRead(ORMBase):
    pat_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    created_at: datetime
    updated_on: datetime


class DoctorCreate(BaseModel):
    name: str
    specialty: str
    reason: Optional[str]
    active: bool


class DoctorRead(ORMBase):
    doc_id: int
    name: str
    specialty: str
    active: bool
    created_at: datetime


class AppointmentCreate(BaseModel):
    patient_id: int = Field(ge=0)
    doctor_id: int = Field(ge=0)
    reason: str = ""
    apt_start: datetime
    apt_duration: int = Field(ge=15, le=180)

    @field_validator("apt_start")
    def timezone_awareness(cls, value: datetime):
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("apt_start must be timezone-aware")
        return value


class AppointmentRead(ORMBase):
    apt_id: int
    patient_id: int
    doctor_id: int
    reason: str
    apt_start: datetime
    duration: int
    apt_created_at: datetime
