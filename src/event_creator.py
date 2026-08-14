"""Create calendar events from natural-language requests using Gemini.

Functions:
- `parse_event_request(nl)` — asks Gemini to extract structured event fields (JSON).
- `build_event_body(parsed)` — converts parsed fields to Google Calendar event body.
- `create_event_from_nl(service, nl)` — end-to-end: parse, confirm, create.
"""
from __future__ import annotations
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import timezone as dt_timezone
from typing import Any, Dict, List, Optional
import re

from src.gemini_client import generate_text
from src.calendar_client import create_event


def _extract_json(text: str) -> str:
    """Try to extract a JSON substring from model output."""
    text = text.strip()
    # Find first '{' and last '}'
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
    prompt = (
        "Extract event information from the user's request.\n"
        "Return ONLY a single valid JSON object with these keys: \n"
        "- summary (string)\n"
        "- date (YYYY-MM-DD) or null\n"
        "- start_time (HH:MM 24-hour) or null\n"
        "- duration_minutes (integer) or null\n"
        "- timezone (IANA string like 'Europe/Lisbon' or null)\n"
        "- attendees (array of email strings, may be empty)\n\n"
        "Important: If the user provides a relative or natural-language date (e.g. 'tomorrow', 'next Monday', 'Aug 14th'), CONVERT it to an explicit date in YYYY-MM-DD format relative to today's date.\n"
        "Use the user's local date rules when interpreting weekdays (assume the system local date if unknown).\n\n"
        "Examples of required output formatting:\n"
        "- If user says 'tomorrow' and today is 2026-08-14, date should be '2026-08-15'.\n"
        "- If user says 'Aug 14' convert to '2026-08-14' if the year is ambiguous and that date is next in the future; otherwise include the explicit year.\n\n"
        "If any information is ambiguous or missing, set the field to null or empty list.\n"
        "If the user does NOT specify a timezone, set the `timezone` field to 'America/Sao_Paulo' (Brazil) in the JSON.\n"
        f"User request: '''{nl}'''\n"
        "Respond with only JSON and no additional text."
    )

    resp = generate_text(prompt)
    json_text = _extract_json(resp)
    try:
        parsed = json.loads(json_text)
        # Ensure timezone is set to default Sao Paulo when model returns null/empty
        if not parsed.get('timezone'):
            parsed['timezone'] = 'America/Sao_Paulo'
        return parsed
    except Exception as e:
        raise RuntimeError(f'Failed to parse model JSON output: {e}\nModel output:\n{resp}')


def build_event_body(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Build a Google Calendar event body from parsed fields."""
    summary = parsed.get('summary') or 'Untitled Event'
    date = parsed.get('date')
    start_time = parsed.get('start_time')
    duration = parsed.get('duration_minutes') or 60
    timezone = parsed.get('timezone') or 'America/Sao_Paulo'
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        # Windows may lack the tzdata package; fall back to fixed -03:00 (Sao Paulo)
        tz = dt_timezone(timedelta(hours=-3))
    attendees = parsed.get('attendees') or []

    if date and start_time:
        # combine into ISO datetime and attach timezone if missing
        # Be robust: the model might return non-ISO or two-digit-year dates.
        start_dt = None
        parse_error = None
        try:
            start_dt = datetime.fromisoformat(f"{date}T{start_time}")
        except Exception as e:
            parse_error = e
            # Try several common date formats (lenient)
            tried = False
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%d/%m/%Y", "%d/%m/%y", "%m/%d/%Y"):
                try:
                    d = datetime.strptime(date, fmt).date()
                    hh, mm = [int(x) for x in start_time.split(":")]
                    start_dt = datetime(d.year, d.month, d.day, hh, mm)
                    tried = True
                    break
                except Exception:
                    continue
            if not tried:
                # Last resort: try extracting numeric parts
                m = re.split(r"[-/\\]", date)
                if len(m) == 3:
                    try:
                        p0, p1, p2 = m
                        # Heuristic: if first token length==4 assume YYYY-MM-DD
                        if len(p0) == 4:
                            year, month, day = int(p0), int(p1), int(p2)
                        else:
                            # assume DD-MM-YY or DD-MM-YYYY
                            day, month, year = int(p0), int(p1), int(p2)
                            if year < 100:
                                # two-digit year -> map to 2000-2099
                                year += 2000
                        hh, mm = [int(x) for x in start_time.split(":")]
                        start_dt = datetime(year, month, day, hh, mm)
                    except Exception:
                        start_dt = None
        if start_dt is None:
            raise RuntimeError(f"Could not parse date/time: date={date} start_time={start_time} (parse error: {parse_error})")
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=tz)
        # Sanity check: if parsed year is far in the past relative to today,
        # but the month/day matches tomorrow, adjust year to the correct one.
        try:
            today = datetime.now(tz).date()
            tomorrow = today + timedelta(days=1)
            if start_dt.date().month == tomorrow.month and start_dt.date().day == tomorrow.day:
                if start_dt.year < tomorrow.year:
                    start_dt = start_dt.replace(year=tomorrow.year)
        except Exception:
            pass
        end_dt = start_dt + timedelta(minutes=int(duration))
        start = {"dateTime": start_dt.isoformat(), "timeZone": timezone}
        end = {"dateTime": end_dt.isoformat(), "timeZone": timezone}
    elif (not date) and start_time:
        # If user provided a time but no date, schedule the next occurrence of that time.
        # Use Sao Paulo timezone (America/Sao_Paulo) by default to build an aware datetime.
        now = datetime.now(tz)
        # parse start_time as HH:MM
        try:
            hh, mm = [int(x) for x in start_time.split(':')]
        except Exception:
            hh, mm = 9, 0
        candidate = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if candidate <= now:
            candidate = candidate + timedelta(days=1)
        end_dt = candidate + timedelta(minutes=int(duration))
        # use ISO with offset and provide timeZone if available
        start = {"dateTime": candidate.isoformat(), "timeZone": timezone}
        end = {"dateTime": end_dt.isoformat(), "timeZone": timezone}
    elif date:
        # all-day event
        start = {"date": date}
        end = {"date": date}
    else:
        # no date — create a tentative event with no time (user should confirm)
        start = {"date": datetime.utcnow().date().isoformat()}
        end = {"date": datetime.utcnow().date().isoformat()}

    event_body: Dict[str, Any] = {
        "summary": summary,
        "start": start,
        "end": end,
    }

    if attendees:
        event_body["attendees"] = [{"email": a} for a in attendees]

    return event_body


def create_event_from_nl(service, nl: str, confirm: bool = True) -> Dict[str, Any]:
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
