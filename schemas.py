"""
Database Schemas for Hospital Management

Each Pydantic model below maps to a MongoDB collection with the
collection name equal to the lowercase class name.

Examples:
- Patient -> "patient"
- Doctor -> "doctor"
- Appointment -> "appointment"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class Patient(BaseModel):
    """
    Patients collection schema
    Collection: "patient"
    """
    first_name: str = Field(..., description="Patient first name")
    last_name: str = Field(..., description="Patient last name")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")
    date_of_birth: Optional[str] = Field(None, description="YYYY-MM-DD")
    gender: Optional[str] = Field(None, description="Male, Female, Other")
    address: Optional[str] = Field(None, description="Home address")
    insurance_provider: Optional[str] = Field(None, description="Insurance company name")
    insurance_number: Optional[str] = Field(None, description="Insurance policy number")
    notes: Optional[str] = Field(None, description="Additional notes")


class Doctor(BaseModel):
    """
    Doctors collection schema
    Collection: "doctor"
    """
    first_name: str = Field(..., description="Doctor first name")
    last_name: str = Field(..., description="Doctor last name")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")
    department: str = Field(..., description="Department or specialty")
    title: Optional[str] = Field(None, description="MD, DO, RN, etc.")


class Appointment(BaseModel):
    """
    Appointments collection schema
    Collection: "appointment"
    """
    patient_id: str = Field(..., description="Patient ObjectId string")
    doctor_id: str = Field(..., description="Doctor ObjectId string")
    start_time: datetime = Field(..., description="Appointment start time (ISO 8601)")
    duration_minutes: int = Field(30, ge=5, le=240, description="Appointment duration in minutes")
    reason: Optional[str] = Field(None, description="Reason for visit")
    status: str = Field("scheduled", description="scheduled|completed|cancelled")
