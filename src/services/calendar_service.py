from datetime import datetime, date, timedelta
from typing import List, Optional
import os
from fastapi import HTTPException
from src.clients.caldav_client import CaldavClient
from src.models.event import Appointment
from dotenv import load_dotenv


load_dotenv()

def get_caldav_client():
    caldav_url = os.environ.get("CALDAV_URL")
    caldav_username = os.environ.get("CALDAV_USERNAME")
    caldav_password = os.environ.get("CALDAV_PASSWORD")
    caldav_calendar_name = os.environ.get("CALDAV_CALENDAR_NAME")

    missing_vars = []
    if not caldav_url:
        missing_vars.append("CALDAV_URL")
    if not caldav_username:
        missing_vars.append("CALDAV_USERNAME")
    if not caldav_password:
        missing_vars.append("CALDAV_PASSWORD")
    if not caldav_calendar_name:
        missing_vars.append("CALDAV_CALENDAR_NAME")

    if missing_vars:
        raise HTTPException(
            status_code=500,
            detail=f"Missing CalDAV environment variables: {', '.join(missing_vars)}"
        )

    try:
        return CaldavClient(
            url_base=caldav_url,
            username=caldav_username,
            password=caldav_password,
            calendar_name=caldav_calendar_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to CalDAV server: {e}")


class CalendarService:
    def __init__(self):
        self.caldav_client = get_caldav_client()

    def create_appointment(self, appointment) -> Appointment:
        try:
            all_events_for_day = self.caldav_client.find_events(
                start=datetime.combine(appointment.start_time.date(), datetime.min.time()),
                end=datetime.combine(appointment.start_time.date(), datetime.max.time())
            )

            new_start = appointment.start_time
            new_end = appointment.end_time

            for event in all_events_for_day:
                vevent = event.vobject_instance.vevent
                existing_start = vevent.dtstart.value
                existing_end = vevent.dtend.value

                if max(new_start, existing_start) < min(new_end, existing_end):
                    raise HTTPException(status_code=409, detail="An appointment already exists in the specified time range.")

            event_uid = self.caldav_client.add_event(
                summary=appointment.summary,
                description=appointment.description,
                start_time=appointment.start_time,
                end_time=appointment.end_time
            )
            return Appointment(uid=event_uid, **appointment.dict())

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create appointment: {e}")

    def get_appointment(self, appointment_id: str) -> Appointment:
        try:
            event = self.caldav_client.get_event_by_uid(appointment_id)
            if not event:
                raise HTTPException(status_code=404, detail="Appointment not found")

            vevent = event.vobject_instance.vevent
            return Appointment(
                uid=appointment_id,
                summary=str(vevent.summary.value),
                description=str(vevent.description.value) if hasattr(vevent, 'description') else None,
                start_time=vevent.dtstart.value,
                end_time=vevent.dtend.value
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve appointment: {e}")

    def list_appointments(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Appointment]:
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
            end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None

            events = self.caldav_client.find_events(start=start_datetime, end=end_datetime)

            appointments = []
            for event in events:
                vevent = event.vobject_instance.vevent
                appointments.append(Appointment(
                    uid=event.url.path.split('/')[-1].split('.')[0],
                    summary=str(vevent.summary.value),
                    description=str(vevent.description.value) if hasattr(vevent, 'description') else None,
                    start_time=vevent.dtstart.value,
                    end_time=vevent.dtend.value
                ))
            return appointments
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list appointments: {e}")

    def update_appointment(self, appointment_id: str, appointment) -> Appointment:
        try:
            all_events_for_day = self.caldav_client.find_events(
                start=datetime.combine(appointment.start_time.date(), datetime.min.time()),
                end=datetime.combine(appointment.start_time.date(), datetime.max.time())
            )

            new_start = appointment.start_time
            new_end = appointment.end_time

            for event in all_events_for_day:
                if event.url.path.split('/')[-1].split('.')[0] == appointment_id:
                    continue
                vevent = event.vobject_instance.vevent
                existing_start = vevent.dtstart.value
                existing_end = vevent.dtend.value

                if max(new_start, existing_start) < min(new_end, existing_end):
                    raise HTTPException(status_code=409,
                                        detail="An appointment already exists in the specified time range.")

            success = self.caldav_client.edit_event(
                uid=appointment_id,
                summary=appointment.summary,
                description=appointment.description,
                start_time=appointment.start_time,
                end_time=appointment.end_time
            )
            if not success:
                raise HTTPException(status_code=404, detail="Appointment not found")
            return Appointment(uid=appointment_id, **appointment.dict())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update appointment: {e}")

    def delete_appointment(self, appointment_id: str):
        try:
            success = self.caldav_client.remove_event_by_uid(appointment_id)
            if not success:
                raise HTTPException(status_code=404, detail="Appointment not found")
            return {"message": "Appointment deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete appointment: {e}")

    def get_free_slots(self, for_date: date) -> List[dict]:
        try:
            now = datetime.now()
            day_start = datetime.combine(for_date, datetime.min.time().replace(hour=9))
            day_end = datetime.combine(for_date, datetime.min.time().replace(hour=17))

            appointments = self.list_appointments(start_date=for_date, end_date=for_date)

            potential_slots = []
            current_time = day_start
            while current_time < day_end:
                potential_slots.append({
                    "start_time": current_time,
                    "end_time": current_time + timedelta(hours=1)
                })
                current_time += timedelta(hours=1)

            free_slots = []
            for slot in potential_slots:
                if slot["start_time"] < now:
                    continue
                is_free = True
                for app in appointments:
                    if max(slot["start_time"], app.start_time) < min(slot["end_time"], app.end_time):
                        is_free = False
                        break
                if is_free:
                    free_slots.append(slot)

            return free_slots
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get free slots: {e}")
