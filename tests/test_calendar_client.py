from unittest.mock import Mock

import pytest

from src import calendar_client


def test_list_upcoming_events_sends_upcoming_query():
    request = Mock()
    request.execute.return_value = {"items": [{"summary": "Planning"}]}
    service = Mock()
    service.events.return_value.list.return_value = request

    result = calendar_client.list_upcoming_events(
        service, max_results=5, calendar_id="work"
    )

    assert result == [{"summary": "Planning"}]
    query = service.events.return_value.list.call_args.kwargs
    assert query["calendarId"] == "work"
    assert query["maxResults"] == 5
    assert query["singleEvents"] is True
    assert query["orderBy"] == "startTime"
    assert query["timeMin"].endswith("+00:00")


def test_list_upcoming_events_returns_empty_list_on_network_error(caplog):
    service = Mock()
    service.events.return_value.list.side_effect = OSError("secret response")

    result = calendar_client.list_upcoming_events(service)

    assert result == []
    assert "secret response" not in caplog.text


@pytest.mark.parametrize(
    "max_results, calendar_id",
    [(0, "primary"), (-1, "primary"), (5, "")],
)
def test_list_upcoming_events_rejects_invalid_arguments(max_results, calendar_id):
    with pytest.raises(ValueError):
        calendar_client.list_upcoming_events(Mock(), max_results, calendar_id)


def test_create_event_returns_api_response():
    service = Mock()
    service.events.return_value.insert.return_value.execute.return_value = {
        "id": "event-1"
    }

    result = calendar_client.create_event(service, {"summary": "Planning"})

    assert result == {"id": "event-1"}
    service.events.return_value.insert.assert_called_once_with(
        calendarId="primary", body={"summary": "Planning"}
    )


def test_create_event_sanitizes_network_error():
    service = Mock()
    service.events.return_value.insert.return_value.execute.side_effect = OSError(
        "token=secret"
    )

    with pytest.raises(RuntimeError, match="Unable to create calendar event") as error:
        calendar_client.create_event(service, {"summary": "Planning"})

    assert "secret" not in str(error.value)


def test_build_calendar_service_rejects_missing_credentials():
    with pytest.raises(ValueError):
        calendar_client.build_calendar_service(None)
