"""Small, typed helpers for interacting with Google Calendar.

Improvements:
- `list_upcoming_events` accepts `calendar_id` and uses `timeMin` to list upcoming events.
- API calls are wrapped to surface clearer errors and avoid crashing the caller.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone as dt_timezone
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


logger = logging.getLogger(__name__)


def build_calendar_service(credentials: Any) -> Any:
    """Build a Google Calendar API service from OAuth credentials."""
    if credentials is None:
        raise ValueError("credentials must not be None")
    try:
        return build('calendar', 'v3', credentials=credentials)
    except Exception as exc:
        raise RuntimeError("Unable to initialize Google Calendar service") from exc


def list_upcoming_events(
    service: Any, max_results: int = 10, calendar_id: str = 'primary'
) -> list[dict[str, Any]]:
    """Return upcoming events from `calendar_id`.

    Uses `timeMin` set to now to avoid returning past events. Returns an empty list
    on API errors (caller may log/raise if desired).
    """
    if max_results < 1:
        raise ValueError("max_results must be greater than zero")
    if not calendar_id.strip():
        raise ValueError("calendar_id must not be empty")

    try:
        now = datetime.now(dt_timezone.utc).isoformat()
        events_result = service.events().list(
            calendarId=calendar_id,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime',
            timeMin=now,
        ).execute()
        return events_result.get('items', [])
    except (HttpError, OSError, TimeoutError):
        logger.warning("Unable to list upcoming calendar events")
        return []


def create_event(
    service: Any, event_body: dict[str, Any], calendar_id: str = 'primary'
) -> dict[str, Any]:
    """Insert an event and return the created event object.

    Raises RuntimeError on API errors so callers can handle/report as needed.
    """
    if not event_body:
        raise ValueError("event_body must not be empty")
    if not calendar_id.strip():
        raise ValueError("calendar_id must not be empty")

    try:
        return service.events().insert(
            calendarId=calendar_id, body=event_body
        ).execute()
    except (HttpError, OSError, TimeoutError) as exc:
        raise RuntimeError("Unable to create calendar event") from exc
