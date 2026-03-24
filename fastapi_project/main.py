from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

# -----------------------------
# DATA
# -----------------------------
doctors = [
    {"id": 1, "name": "Dr A", "specialization": "General", "available": True},
    {"id": 2, "name": "Dr B", "specialization": "Dentist", "available": True},
    {"id": 3, "name": "Dr C", "specialization": "Skin", "available": False}
]

appointments = []
counter = 1


# -----------------------------
# HOME
# -----------------------------
@app.get("/")
def home():
    return {"message": "AI Medical Appointment System Running"}


# -----------------------------
# GET ALL DOCTORS
# -----------------------------
@app.get("/doctors")
def get_doctors():
    return {"total": len(doctors), "data": doctors}


# -----------------------------
# SUMMARY (IMPORTANT ORDER)
# -----------------------------
@app.get("/doctors/summary")
def summary():
    total = len(doctors)
    available = len([d for d in doctors if d["available"]])
    unavailable = total - available
    specializations = list(set([d["specialization"] for d in doctors]))

    return {
        "total": total,
        "available": available,
        "unavailable": unavailable,
        "specializations": specializations
    }


# -----------------------------
# GET DOCTOR BY ID
# -----------------------------
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    for d in doctors:
        if d["id"] == doctor_id:
            return d
    return {"error": "Doctor not found"}


# -----------------------------
# GET APPOINTMENTS
# -----------------------------
@app.get("/appointments")
def get_appointments():
    return {"total": len(appointments), "data": appointments}


# -----------------------------
# PYDANTIC MODEL
# -----------------------------
class AppointmentRequest(BaseModel):
    name: str = Field(min_length=2)
    doctor_id: int = Field(gt=0)
    time: str


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def find_doctor(doc_id):
    for d in doctors:
        if d["id"] == doc_id:
            return d
    return None


def check_availability(doctor_id, time):
    for a in appointments:
        if a["doctor_id"] == doctor_id and a["time"] == time:
            return False
    return True


# -----------------------------
# BOOK APPOINTMENT
# -----------------------------
@app.post("/book")
def book(app_data: AppointmentRequest):
    global counter

    doctor = find_doctor(app_data.doctor_id)

    if not doctor:
        return {"error": "Doctor not found"}

    if not doctor["available"]:
        return {"error": "Doctor not available"}

    if not check_availability(app_data.doctor_id, app_data.time):
        return {"error": "Time slot already booked"}

    appointment = {
        "id": counter,
        "name": app_data.name,
        "doctor_id": app_data.doctor_id,
        "time": app_data.time,
        "status": "booked"
    }

    appointments.append(appointment)
    counter += 1

    return appointment


# -----------------------------
# FILTER DOCTORS
# -----------------------------
@app.get("/doctors/filter")
def filter_doctors(specialization: str = Query(None)):
    result = doctors

    if specialization is not None:
        result = [d for d in result if d["specialization"] == specialization]

    return {"count": len(result), "data": result}


# -----------------------------
# ADD DOCTOR
# -----------------------------
@app.post("/doctors")
def add_doctor(doc: dict):
    doc["id"] = len(doctors) + 1
    doctors.append(doc)
    return doc


# -----------------------------
# UPDATE DOCTOR
# -----------------------------
@app.put("/doctors/{id}")
def update_doctor(id: int, available: bool = None):
    doc = find_doctor(id)

    if not doc:
        return {"error": "Doctor not found"}

    if available is not None:
        doc["available"] = available

    return doc


# -----------------------------
# DELETE DOCTOR
# -----------------------------
@app.delete("/doctors/{id}")
def delete_doctor(id: int):
    doc = find_doctor(id)

    if not doc:
        return {"error": "Doctor not found"}

    doctors.remove(doc)
    return {"message": "Doctor deleted"}


# -----------------------------
# SEARCH DOCTORS
# -----------------------------
@app.get("/doctors/search")
def search_doctors(keyword: str):
    result = [
        d for d in doctors
        if keyword.lower() in d["name"].lower()
        or keyword.lower() in d["specialization"].lower()
    ]

    if not result:
        return {"message": "No doctors found"}

    return {"total_found": len(result), "data": result}


# -----------------------------
# SORT DOCTORS
# -----------------------------
@app.get("/doctors/sort")
def sort_doctors(order: str = "asc"):
    return sorted(doctors, key=lambda x: x["name"], reverse=(order == "desc"))


# -----------------------------
# PAGINATION
# -----------------------------
@app.get("/doctors/page")
def paginate(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit

    total = len(doctors)
    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "data": doctors[start:end]
    }


# -----------------------------
# COMBINED BROWSE
# -----------------------------
@app.get("/doctors/browse")
def browse(keyword: str = None, order: str = "asc", page: int = 1, limit: int = 2):
    result = doctors

    if keyword:
        result = [d for d in result if keyword.lower() in d["name"].lower()]

    result = sorted(result, key=lambda x: x["name"], reverse=(order == "desc"))

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": len(result),
        "data": result[start:end]
    }


# -----------------------------
# APPOINTMENT STATUS (ADVANCED)
# -----------------------------
@app.put("/appointments/confirm/{id}")
def confirm(id: int):
    for a in appointments:
        if a["id"] == id:
            a["status"] = "confirmed"
            return a
    return {"error": "Appointment not found"}


@app.put("/appointments/cancel/{id}")
def cancel(id: int):
    for a in appointments:
        if a["id"] == id:
            a["status"] = "cancelled"
            return a
    return {"error": "Appointment not found"}


# -----------------------------
# AI RECOMMENDATION (ADVANCED)
# -----------------------------
@app.post("/recommend")
def recommend(symptom: str):
    mapping = {
        "fever": "General",
        "tooth": "Dentist",
        "skin": "Skin",
        "eye": "Ophthalmologist"
    }

    result = mapping.get(symptom.lower(), "General")

    return {
        "symptom": symptom,
        "recommended_specialization": result
    }


# -----------------------------
# ANALYTICS (ADVANCED)
# -----------------------------
@app.get("/analytics")
def analytics():
    total = len(appointments)
    confirmed = len([a for a in appointments if a["status"] == "confirmed"])
    cancelled = len([a for a in appointments if a["status"] == "cancelled"])

    return {
        "total_appointments": total,
        "confirmed": confirmed,
        "cancelled": cancelled
    }


# -----------------------------
# TOP DOCTOR (BONUS)
# -----------------------------
@app.get("/top-doctor")
def top_doctor():
    count = {}

    for a in appointments:
        doc_id = a["doctor_id"]
        count[doc_id] = count.get(doc_id, 0) + 1

    if not count:
        return {"message": "No bookings yet"}

    top = max(count, key=count.get)

    return {
        "doctor_id": top,
        "bookings": count[top]
    }