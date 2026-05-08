#step-1 : import database
from database import engine, init_db, User, SessionLocal, get_db
from typing import Optional, ClassVar


init_db()  # Initialize the database and create tables if they don't exist

#step3 : data contrast using pydantic models
import datetime as dt
from pydantic import BaseModel
class AppointmentRequest(BaseModel):
    patient_name: str
    reason: str
    start_time: dt.datetime 

class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    reason: str
    start_time: dt.datetime
    canceled: bool
    created_at: dt.datetime

class CancelAppointmentRequest(BaseModel):
    patient_name: str
    date: dt.date
    appointment_id: Optional[int] = None 

#class CancelAppointmentResponse(BaseModel):
#canceled_cnt:int
from typing import ClassVar

class CancelAppointmentResponse(BaseModel):
    patient_name: str
    canceled_cnt: int
     # Not treated as a Pydantic field
   

#step-2 : create fast api endpoits 

from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy.orm import Session

app = FastAPI()
"""
@app.get("/")
def root():
    return {"message": "Appointment API is running! Visit /docs for the API documentation."}

"""

#----> schedule appointment
@app.post("/schedule_appointments/")
def schedule_appointment(request: AppointmentRequest,db:Session=Depends(get_db)):
    #logic to schedule appointemnt , write row to database
    new_appointment = User(
        patient_name=request.patient_name,
        reason=request.reason,
        start_time=request.start_time
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)  # Refresh to get the generated ID and other fields
    new_appointment_response = AppointmentResponse(
        id=new_appointment.id,
        patient_name=new_appointment.patient_name,
        reason=new_appointment.reason,
        start_time=new_appointment.start_time,
        canceled=new_appointment.canceled,
        created_at=new_appointment.created_at
    )
    return new_appointment_response
#-->cancel appointment
"""
from sqlalchemy import select
@app.post("/cancel_appointment/")
def cancel_appointment(request: CancelAppointmentRequest, db: Session = Depends(get_db)):
    start_date=dt.datetime.combine(request.date, dt.time.min)  # Start of the day
    end_date=start_date+dt.timedelta(days=1)

    result = db.execute(
        select(User)
        .where(User.patient_name == request.patient_name)
        .where(User.start_time >= start_date)
        .where(User.start_time < end_date)
        .where(User.canceled == False)
    )
    appointments = result.scalars().all()
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointment found to cancel")
    for appointment in appointments:
        #print(f"Cancelling appointment ID: {appointment.id} for patient: {appointment.patient_name} at {appointment.start_time}")
        appointment.canceled = True

    db.commit()
    #logic to cancel appointment, update canceled row to true
    return  CancelAppointmentResponse(
        patient_name=request.patient_name,
        canceled_cnt=len(appointments)
    )

    #return CancelAppointmentResponse(canceled_cnt=len(appointments))
"""
from sqlalchemy import select
@app.post("/cancel_appointment/")
def cancel_appointment(request: CancelAppointmentRequest, db: Session = Depends(get_db)):
    
    # If appointment_id is provided, cancel that specific one
    if request.appointment_id is not None:
        appointment = db.get(User, request.appointment_id)
        if not appointment or appointment.canceled:
            raise HTTPException(status_code=404, detail="Appointment not found")
        appointment.canceled = True
        db.commit()
        return CancelAppointmentResponse(
            patient_name=appointment.patient_name,
            canceled_cnt=1
        )

    # Otherwise fall back to name + date (your existing logic)
    start_date = dt.datetime.combine(request.date, dt.time.min)
    end_date = start_date + dt.timedelta(days=1)

    result = db.execute(
        select(User)
        .where(User.patient_name == request.patient_name)
        .where(User.start_time >= start_date)
        .where(User.start_time < end_date)
        .where(User.canceled == False)
    )
    appointments = result.scalars().all()
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointment found to cancel")
    
    for appointment in appointments:
        appointment.canceled = True

    db.commit()
    return CancelAppointmentResponse(
        patient_name=request.patient_name,
        canceled_cnt=len(appointments)
    )

"""
from datetime import date
import datetime as dt
@app.get("/debug_appointments/")
def debug_appointments(db: Session = Depends(get_db)):
    result = db.execute(select(User))
    all_appointments = result.scalars().all()
    return [
        {
            "id": a.id,
            "patient_name": a.patient_name,
            "start_time": str(a.start_time),
            "canceled": a.canceled
        }
        for a in all_appointments
    ]
"""
@app.get("/list_appointments/")
def list_appointments(
    date: dt.date,
    db: Session = Depends(get_db)
):
    booked_appointments = []

    # Start and end of selected day
    start_date = dt.datetime.combine(date, dt.time.min)
    end_date = start_date + dt.timedelta(days=1)

    result = db.execute(
        select(User)
        .where(User.canceled.is_(False))
        .where(User.start_time >= start_date)
        .where(User.start_time < end_date)
        .order_by(User.start_time.asc())
    )

    for appointment in result.scalars().all():

        booked_appointments.append(
            AppointmentResponse(
                id=appointment.id,
                patient_name=appointment.patient_name,
                reason=appointment.reason,
                start_time=appointment.start_time,
                canceled=appointment.canceled,
                created_at=appointment.created_at
            )
        )

    return booked_appointments

import uvicorn
if __name__=="__main__":
    uvicorn.run("backend:app",host="127.0.0.1",port=8000,reload=True)

#step5: test the endpoints using streamlit or postman



