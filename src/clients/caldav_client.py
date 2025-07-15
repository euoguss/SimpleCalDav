from caldav import DAVClient
from datetime import datetime, timedelta
from pytz import timezone
import vobject
from typing import Optional


class CaldavClient:
    def __init__(self, url_base: str, username: str, password: str, calendar_name: str):
        self.client = DAVClient(
            url=url_base,
            username=username,
            password=password
        )
        self.principal = self.client.principal()
        self.calendar = self.principal.calendar(name=calendar_name)

    def find_events(self, start: Optional[datetime] = None, end: Optional[datetime] = None):
        if not start:
            start = datetime.now()
        if not end:
            end = start + timedelta(days=30)
        events = self.calendar.date_search(start=start, end=end)
        return events

    def get_event_by_uid(self, uid: str):
        event = self.calendar.event_by_uid(uid)
        return event

    def add_event(self, summary: str, description: Optional[str], start_time: datetime, end_time: datetime):
        vcalendar = vobject.iCalendar()
        vevent = vcalendar.add("vevent")
        vevent.add("summary").value = summary
        if description:
            vevent.add("description").value = description
        vevent.add("dtstart").value = start_time
        vevent.add("dtend").value = end_time
        vevent.add("dtstamp").value = datetime.now(timezone("UTC"))
        event = self.calendar.save_event(ical=vcalendar.serialize())
        return event.url.path.split('/')[-1].split('.')[0]

    def edit_event(self, uid: str, summary: Optional[str] = None, description: Optional[str] = None, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None):
        event = self.get_event_by_uid(uid)
        if not event:
            return False

        vevent = event.vobject_instance.vevent

        if summary is not None:
            vevent.summary.value = summary
        if description is not None:
            vevent.description.value = description
        elif hasattr(vevent, 'description'):
            del vevent.description
        if start_time is not None:
            vevent.dtstart.value = start_time
        if end_time is not None:
            vevent.dtend.value = end_time

        event.save()
        return True

    def remove_event_by_uid(self, uid: str):
        event = self.get_event_by_uid(uid)
        if not event:
            return False
        event.delete()
        return True