from fastapi import APIRouter, Depends
from typing import List, Optional
from datetime import date

from src.models.event import Appointment, FreeSlot
from src.services.calendar_service import CalendarService

router = APIRouter()


def get_calendar_service():
    return CalendarService()


@router.get("/appointments/free_slots/", response_model=List[FreeSlot])
async def get_free_slots(for_date: date, service: CalendarService = Depends(get_calendar_service)):
    return service.get_free_slots(for_date)


@router.post("/appointments/", response_model=Appointment)
async def create_appointment(appointment: Appointment, service: CalendarService = Depends(get_calendar_service)):
    return service.create_appointment(appointment)


@router.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str, service: CalendarService = Depends(get_calendar_service)):
    return service.get_appointment(appointment_id)


@router.get("/appointments/", response_model=List[Appointment])
async def list_appointments(start_date: Optional[date] = None, end_date: Optional[date] = None, service: CalendarService = Depends(get_calendar_service)):
    return service.list_appointments(start_date, end_date)


@router.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, appointment: Appointment, service: CalendarService = Depends(get_calendar_service)):
    return service.update_appointment(appointment_id, appointment)


@router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: str, service: CalendarService = Depends(get_calendar_service)):
    return service.delete_appointment(appointment_id)
