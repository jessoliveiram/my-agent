from unittest.mock import Mock

import pytest

from src import event_creator


def test_build_event_body_creates_timezone_aware_event():
    parsed = {
        "summary": "Review",
        "date": "2026-08-22",
        "start_time": "10:30",
        "duration_minutes": 30,
        "timezone": "America/Sao_Paulo",
        "attendees": ["ana@example.com"],
    }

    result = event_creator.build_event_body(parsed)

    assert result["summary"] == "Review"
    assert result["start"] == {
        "dateTime": "2026-08-22T10:30:00-03:00",
        "timeZone": "America/Sao_Paulo",
    }
    assert result["end"] == {
        "dateTime": "2026-08-22T11:00:00-03:00",
        "timeZone": "America/Sao_Paulo",
    }
    assert result["attendees"] == [{"email": "ana@example.com"}]


@pytest.mark.parametrize(
    "parsed",
    [
        {"date": "tomorrow"},
        {"date": "2026-02-30"},
        {"date": "2026-08-22", "start_time": "25:00"},
        {"date": "2026-08-22", "timezone": "Not/AZone"},
        {"date": "2026-08-22", "duration_minutes": 0},
    ],
)
def test_build_event_body_rejects_invalid_schedule(parsed):
    with pytest.raises(ValueError):
        event_creator.build_event_body(parsed)


def test_parse_event_request_resolves_relative_date_in_single_prompt(monkeypatch):
    response = (
        '{"summary":"Planning","date":"2026-08-22",'
        '"start_time":"10:00","duration_minutes":60,'
        '"timezone":"America/Sao_Paulo","attendees":[]}'
    )
    generate_text = Mock(return_value=response)
    monkeypatch.setattr(event_creator, "generate_text", generate_text)

    result = event_creator.parse_event_request("tomorrow at 10am")

    assert result["date"] == "2026-08-22"
    prompt = generate_text.call_args.args[0]
    assert "Reference date is " in prompt
    assert "Convert 'today', 'tomorrow', weekdays" in prompt
    assert generate_text.call_count == 1


def test_parse_event_request_does_not_expose_invalid_model_output(monkeypatch):
    secret_output = '{"token":"do-not-log"'
    monkeypatch.setattr(event_creator, "generate_text", lambda _: secret_output)

    with pytest.raises(RuntimeError) as error:
        event_creator.parse_event_request("create event")

    assert "do-not-log" not in str(error.value)


def test_parse_event_request_rejects_empty_request():
    with pytest.raises(ValueError):
        event_creator.parse_event_request("   ")


def test_create_event_from_nl_can_skip_confirmation(monkeypatch, capsys):
    parsed = {
        "summary": "Planning",
        "date": "2026-08-22",
        "start_time": "10:00",
        "duration_minutes": 30,
        "timezone": "America/Sao_Paulo",
        "attendees": [],
    }
    created = {"htmlLink": "https://calendar.example/event"}
    monkeypatch.setattr(event_creator, "parse_event_request", lambda _: parsed)
    create_event = Mock(return_value=created)
    monkeypatch.setattr(event_creator, "create_event", create_event)

    result = event_creator.create_event_from_nl(Mock(), "planning", confirm=False)

    assert result == created
    create_event.assert_called_once()
    assert "Planning" in capsys.readouterr().out
