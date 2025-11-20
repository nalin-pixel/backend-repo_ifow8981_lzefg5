import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Patient, Doctor, Appointment

try:
    from bson import ObjectId
except Exception:  # bson is provided by pymongo
    ObjectId = None  # type: ignore


app = FastAPI(title="Hospital Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helpers
class CreatePatientRequest(Patient):
    pass


class CreateDoctorRequest(Doctor):
    pass


class CreateAppointmentRequest(Appointment):
    pass


def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in doc.items():
        if k == "_id":
            out["id"] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


@app.get("/")
def read_root():
    return {"message": "Hospital Management API is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, "name", None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:  # pragma: no cover
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# Patients
@app.post("/patients")
def create_patient(payload: CreatePatientRequest):
    patient_id = create_document("patient", payload)
    return {"id": patient_id}


@app.get("/patients")
def list_patients(limit: Optional[int] = 100) -> List[Dict[str, Any]]:
    docs = get_documents("patient", {}, limit)
    return [serialize_doc(d) for d in docs]


# Doctors
@app.post("/doctors")
def create_doctor(payload: CreateDoctorRequest):
    doctor_id = create_document("doctor", payload)
    return {"id": doctor_id}


@app.get("/doctors")
def list_doctors(limit: Optional[int] = 100) -> List[Dict[str, Any]]:
    docs = get_documents("doctor", {}, limit)
    return [serialize_doc(d) for d in docs]


# Appointments
@app.post("/appointments")
def create_appointment(payload: CreateAppointmentRequest):
    # Basic referential checks (best-effort)
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # Ensure referenced patient and doctor exist (optional best-effort)
    try:
        pid = payload.patient_id
        did = payload.doctor_id
        patient_exists = db["patient"].find_one({"_id": ObjectId(pid)}) if ObjectId else True
        doctor_exists = db["doctor"].find_one({"_id": ObjectId(did)}) if ObjectId else True
        if not patient_exists:
            raise HTTPException(status_code=404, detail="Patient not found")
        if not doctor_exists:
            raise HTTPException(status_code=404, detail="Doctor not found")
    except Exception:
        # If ObjectId conversion fails, still allow insert; IDs may be strings in some envs
        pass

    appt_id = create_document("appointment", payload)
    return {"id": appt_id}


@app.get("/appointments")
def list_appointments(limit: Optional[int] = 100) -> List[Dict[str, Any]]:
    docs = get_documents("appointment", {}, limit)
    return [serialize_doc(d) for d in docs]


@app.get("/stats")
def get_stats():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        return {
            "patients": db["patient"].count_documents({}),
            "doctors": db["doctor"].count_documents({}),
            "appointments": db["appointment"].count_documents({}),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
