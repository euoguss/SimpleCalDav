from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AppointmentBase(BaseModel):
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

class Appointment(AppointmentBase):
    uid: str

class FreeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
