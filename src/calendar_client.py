"""Simple Google Calendar client helpers with small robustness improvements.

Improvements:
- `list_upcoming_events` accepts `calendar_id` and uses `timeMin` to list upcoming events.
- API calls are wrapped to surface clearer errors and avoid crashing the caller.
"""
from __future__ import print_function
from datetime import datetime, timezone as dt_timezone
from googleapiclient.discovery import build


def build_calendar_service(credentials):
    service = build('calendar', 'v3', credentials=credentials)
    return service


def list_upcoming_events(service, max_results=10, calendar_id='primary'):
    """Return upcoming events from `calendar_id`.

    Uses `timeMin` set to now to avoid returning past events. Returns an empty list
    on API errors (caller may log/raise if desired).
    """
    try:
        now = datetime.utcnow().replace(tzinfo=dt_timezone.utc).isoformat()
        events_result = service.events().list(
            calendarId=calendar_id,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime',
            timeMin=now,
        ).execute()
        events = events_result.get('items', [])
        return events
    except Exception as e:
        # surface a helpful message but return an empty list to keep callers simple
        print(f"Warning: failed to list upcoming events: {e}")
        return []


def create_event(service, event_body: dict, calendar_id='primary'):
    """Insert an event and return the created event object.

    Raises RuntimeError on API errors so callers can handle/report as needed.
    """
    try:
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        return event
    except Exception as e:
        raise RuntimeError(f"Failed to create calendar event: {e}") from e
