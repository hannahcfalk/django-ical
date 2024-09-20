import requests
from icalendar import Calendar
from datetime import datetime


def fetch_icalendar_events(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    calendar = Calendar.from_ical(response.content)
    events = []

    for component in calendar.walk():
        if component.name == "VEVENT":
            event = {
                "summary": component.get("summary"),
                "description": component.get("description"),
                "start": component.get("dtstart").dt,
                "end": component.get("dtend").dt,
            }
            events.append(event)

    return events
