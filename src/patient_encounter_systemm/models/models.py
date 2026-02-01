from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from patient_encounter_systemm.database import Base


class Patient(Base):
    """
    Represents a patient in the hospital.
    """

    __tablename__ = "varun_patients"

    pat_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    # pylint: disable=not-callable
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # pylint: disable=not-callable
    updated_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # One-to-many relationship: one patient -> many appointments
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )


class Doctor(Base):
    """
    Represents a doctor in the hospital.
    """

    __tablename__ = "varun_doctors"

    doc_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    active_status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # pylint: disable=not-callable
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")


class Appointment(Base):
    """
    Represents an appointment between a patient and a doctor.
    """

    __tablename__ = "varun_appointments"

    apt_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("varun_patients.pat_id"), nullable=False
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("varun_doctors.doc_id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String(200))
    apt_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    apt_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    # pylint: disable=not-callable
    apt_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    patient: Mapped[Patient] = relationship(back_populates="appointments")
    doctor: Mapped[Doctor] = relationship(back_populates="appointments")

    Index("idx_appointment_doctor_start", "doctor_id", "apt_start")
