from django.urls import path
from .views import display_apple_calendar_events
from .views import EventFeed, authorize, callback

urlpatterns = [
    path("ical/", EventFeed(), name="event_feed"),
    path("authorize/", authorize, name="authorize"),
    path("callback/", callback, name="callback"),
    path(
        "apple-calendar/",
        display_apple_calendar_events,
        name="display_apple_calendar_events",
    ),
]
