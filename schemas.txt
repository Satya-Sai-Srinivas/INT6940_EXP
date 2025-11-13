from pydantic import BaseModel

# This file defines the "shape" of data for your API.

class ClinicianOverview(BaseModel):
    """
    Represents the statistical overview for a single clinician.
    This is what the API will return.
    """
    id: int
    full_name: str
    patient_count: int
    appointment_count: int

    class Config:
        # This allows the Pydantic model to read data from
        # SQLAlchemy models (replaces orm_mode = True)
        from_attributes = True