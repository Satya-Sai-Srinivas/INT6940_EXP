from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

# --- PLEASE UPDATE THIS FILE ---
#
# I need your actual table names and columns from your database
# to build these models. Below is just a *GUESS* based on your request.
#
# Please correct 'clinicians' and 'appointments' with your real table names
# and column names.
#
# --- END OF INSTRUCTIONS ---


# class Clinician(Base):
#     __tablename__ = "clinicians"  # <-- Is this correct?
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String) # <-- Is this 'name', 'full_name'?
#     specialty = Column(String) # <-- Do you have this?
#
#     # This assumes you have an 'appointments' table
#     # and it has a 'clinician' property
#     appointments = relationship("Appointment", back_populates="clinician")

# class Appointment(Base):
#     __tablename__ = "appointments" # <-- Is this correct?
#
#     id = Column(Integer, primary_key=True)
#     appointment_date = Column(DateTime)
#
#     # --- Foreign Keys (How tables link) ---
#     clinician_id = Column(Integer, ForeignKey("clinicians.id"))
#     patient_id = Column(Integer, ForeignKey("patients.id"))
#
#     # --- Relationships (How SQLAlchemy links) ---
#     clinician = relationship("Clinician", back_populates="appointments")
#     patient = relationship("Patient", back_populates="appointments")

# class Patient(Base):
#     __tablename__ = "patients" # <-- Is this correct?
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#
#     appointments = relationship("Appointment", back_populates="patient")