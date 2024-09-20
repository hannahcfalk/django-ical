from django_ical.views import ICalFeed
from .models import Event
from django.shortcuts import render, redirect
from .utils import fetch_icalendar_events
import caldav
from caldav import DAVClient
from django.http import HttpResponse
from requests_oauthlib import OAuth2Session
import os


class EventFeed(ICalFeed):
    product_id = "-//example.com//Example//EN"
    timezone = "UTC"
    file_name = "event.ics"

    def items(self):
        return Event.objects.all()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_start_datetime(self, item):
        return item.start_datetime


# OAuth 2.0 credentials
client_id = os.getenv("APPLE_CLIENT_ID")
client_secret = os.getenv("APPLE_CLIENT_SECRET")
redirect_uri = "https://yourdomain.com/callback"

# OAuth 2.0 endpoints
authorization_base_url = "https://appleid.apple.com/auth/authorize"
token_url = "https://appleid.apple.com/auth/token"


def authorize(request):
    apple = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=["calendar"])
    authorization_url, state = apple.authorization_url(authorization_base_url)
    request.session["oauth_state"] = state
    return redirect(authorization_url)


def callback(request):
    apple = OAuth2Session(
        client_id, state=request.session["oauth_state"], redirect_uri=redirect_uri
    )
    token = apple.fetch_token(
        token_url,
        client_secret=client_secret,
        authorization_response=request.build_absolute_uri(),
    )
    request.session["oauth_token"] = token
    return redirect("display_apple_calendar_events")


def display_apple_calendar_events(request):
    client = DAVClient(
        url="https://caldav.icloud.com/",
        username=os.getenv("APPLE_ID_EMAIL"),
        password=os.getenv("APP_SPECIFIC_PASSWORD"),
    )

    principal = client.principal()
    print(f"Client: {client}")
    print(f"Principal: {principal}")
    calendars = principal.calendars()

    events = []
    for calendar in calendars:
        print(f"Calendar: {calendar.name}")
        cal_events = calendar.events()
        for event in cal_events:
            events.append(
                Event.objects.create(
                    title=event.vobject_instance.vevent.summary.value,
                )
            )
    return HttpResponse(f"Events: {events}")


def display_apple_calendar_events_oauth(request):
    token = request.session.get("oauth_token")
    if not token:
        return redirect("authorize")

    apple = OAuth2Session(client_id, token=token)
    headers = {
        "Authorization": f'Bearer {token["access_token"]}',
    }

    # Connect to Apple Calendar via CalDAV using OAuth token
    client = DAVClient(
        url="https://caldav.icloud.com/",  # Apple's CalDAV URL
        headers=headers,
    )

    principal = client.principal()
    print(f"Client: {client}")
    print(f"Principal: {principal}")
    # Retrieve calendars associated with the account
    calendars = principal.calendars()

    # Get calendar events
    events = []
    for calendar in calendars:
        print(f"Calendar: {calendar.name}")
        cal_events = calendar.events()
        for event in cal_events:
            events.append(
                Event.objects.create(
                    title=event.vobject_instance.vevent.summary.value,
                )
            )
    return HttpResponse(f"Events: {events}")
