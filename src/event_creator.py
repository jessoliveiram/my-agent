"""Create calendar events from natural-language requests using Gemini.

Functions:
- `parse_event_request(nl)` — asks Gemini to extract structured event fields (JSON).
- `build_event_body(parsed)` — converts parsed fields to Google Calendar event body.
- `create_event_from_nl(service, nl)` — end-to-end: parse, confirm, create.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from typing import Any, Dict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.gemini_client import generate_text
from src.calendar_client import create_event


logger = logging.getLogger(__name__)


def _extract_json(text: str) -> str:
    """Try to extract a JSON substring from model output."""
    text = text.strip()

    # Strip code fences if the model wraps JSON in markdown.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text


def parse_event_request(nl: str) -> Dict[str, Any]:
    """Ask Gemini to extract event fields and return a dict.

    The returned dict keys: summary, date (YYYY-MM-DD or null), start_time (HH:MM or null),
    duration_minutes (int or null), timezone (string or null), attendees (list of emails).
    """
    if not nl.strip():
        raise ValueError("Natural-language event request must not be empty")

    reference_date = datetime.now(dt_timezone.utc).date().isoformat()
    prompt = (
        "Extract event information from the user's request.\n"
        "Return ONLY one valid JSON object with exactly these keys:\n"
        "- summary (string)\n"
        "- date (YYYY-MM-DD) or null\n"
        "- start_time (HH:MM 24-hour) or null\n"
        "- duration_minutes (integer) or null\n"
        "- timezone (IANA string like 'Europe/Lisbon' or null)\n"
        "- attendees (array of email strings, may be empty)\n\n"
        "Rules:\n"
        f"- Reference date is {reference_date} in UTC. Use it to resolve relative dates.\n"
        "- Convert 'today', 'tomorrow', weekdays and month/day expressions to an explicit date.\n"
        "- For a month/day without a year, choose the next occurrence on or after the reference date.\n"
        "- Use 24-hour HH:MM for start_time and an integer for duration_minutes.\n"
        "- Use an IANA timezone; if none is provided, use 'America/Sao_Paulo'.\n"
        "- If a value is missing or genuinely ambiguous, use null; attendees must be an array.\n"
        "- Do not include Markdown, explanations, or extra keys.\n\n"
        f"User request: '''{nl}'''\n"
        "Respond with only JSON and no additional text."
    )

    resp = generate_text(prompt)
    json_text = _extract_json(resp)
    try:
        parsed = json.loads(json_text)
        if not isinstance(parsed, dict):
            raise ValueError("model output must be a JSON object")
        timezone_name = parsed.get('timezone') or 'America/Sao_Paulo'
        parsed['timezone'] = timezone_name
        return parsed
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        logger.warning("Gemini returned an invalid event payload")
        raise RuntimeError("Failed to parse model JSON output") from exc


def build_event_body(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Build a Google Calendar event body from parsed fields."""
    if not isinstance(parsed, dict):
        raise TypeError("parsed event must be a dictionary")

    summary = parsed.get('summary') or 'Untitled Event'
    timezone = parsed.get('timezone') or 'America/Sao_Paulo'
    date = parsed.get('date')
    if date is not None:
        if not isinstance(date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            raise ValueError("date must use YYYY-MM-DD format")
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("date must be a valid calendar date") from exc
    start_time = parsed.get('start_time')
    duration_value = parsed.get('duration_minutes')
    try:
        duration = 60 if duration_value is None else int(duration_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("duration_minutes must be an integer") from exc
    if duration <= 0:
        raise ValueError("duration_minutes must be greater than zero")
    if not isinstance(timezone, str) or not timezone.strip():
        raise ValueError("timezone must be a non-empty IANA timezone")
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("timezone must be a valid IANA timezone") from exc
    attendees = parsed.get('attendees') or []

    if date and start_time:
        if not isinstance(start_time, str):
            raise ValueError("start_time must use HH:MM format")
        try:
            start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        except ValueError as exc:
            raise ValueError("start_time must use valid 24-hour HH:MM format") from exc
        start_dt = start_dt.replace(tzinfo=tz)
        end_dt = start_dt + timedelta(minutes=duration)
        start = {"dateTime": start_dt.isoformat(), "timeZone": timezone}
        end = {"dateTime": end_dt.isoformat(), "timeZone": timezone}
    elif (not date) and start_time:
        # If user provided a time but no date, schedule the next occurrence of that time.
        # Use Sao Paulo timezone (America/Sao_Paulo) by default to build an aware datetime.
        now = datetime.now(tz)
        try:
            parsed_time = datetime.strptime(start_time, "%H:%M")
        except (TypeError, ValueError) as exc:
            raise ValueError("start_time must use valid 24-hour HH:MM format") from exc
        hh, mm = parsed_time.hour, parsed_time.minute
        candidate = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if candidate <= now:
            candidate = candidate + timedelta(days=1)
        end_dt = candidate + timedelta(minutes=duration)
        # use ISO with offset and provide timeZone if available
        start = {"dateTime": candidate.isoformat(), "timeZone": timezone}
        end = {"dateTime": end_dt.isoformat(), "timeZone": timezone}
    elif date:
        # all-day event
        start = {"date": date}
        try:
            start_date = datetime.strptime(date, "%Y-%m-%d").date()
            end_date = start_date + timedelta(days=1)
            end = {"date": end_date.isoformat()}
        except ValueError:
            end = {"date": date}
    else:
        # no date — create a tentative event with no time (user should confirm)
        today = datetime.now(dt_timezone.utc).date().isoformat()
        start = {"date": today}
        end = {"date": today}

    event_body: Dict[str, Any] = {
        "summary": summary,
        "start": start,
        "end": end,
    }

    if attendees:
        event_body["attendees"] = [{"email": a} for a in attendees]

    return event_body


def create_event_from_nl(service: Any, nl: str, confirm: bool = True) -> dict[str, Any]:
    """Parse NL request, show parsed fields, optionally confirm, and create event."""
    parsed = parse_event_request(nl)
    body = build_event_body(parsed)

    # Show parsed result to user for confirmation
    print('\nParsed event:')
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    print('\nEvent body to be created:')
    print(json.dumps(body, indent=2, ensure_ascii=False))

    # Compute human-friendly start/end for confirmation
    start = body.get('start', {})
    end = body.get('end', {})
    start_str = ''
    end_str = ''
    try:
        if 'dateTime' in start:
            dt = datetime.fromisoformat(start['dateTime'])
            start_str = dt.isoformat()
        elif 'date' in start:
            start_str = start['date'] + ' (all-day)'
    except Exception:
        start_str = str(start)
    try:
        if 'dateTime' in end:
            dt2 = datetime.fromisoformat(end['dateTime'])
            end_str = dt2.isoformat()
        elif 'date' in end:
            end_str = end['date'] + ' (all-day)'
    except Exception:
        end_str = str(end)

    attendees_list = [a.get('email') for a in body.get('attendees', [])] if body.get('attendees') else []
    print('\nComputed schedule:')
    print(f"- Summary: {body.get('summary')}")
    print(f"- Start: {start_str}")
    print(f"- End:   {end_str}")
    if attendees_list:
        print(f"- Attendees: {', '.join(attendees_list)}")

    if confirm:
        ans = input('\nCreate this event? (y/N): ').strip().lower()
        if ans != 'y':
            print('Aborted by user.')
            return {}

    created = create_event(service, body)
    print('Event created: ', created.get('htmlLink'))
    return created
