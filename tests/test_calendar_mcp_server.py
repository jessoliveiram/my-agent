from unittest.mock import Mock, patch

import pytest

from src import calendar_mcp_server


def test_upcoming_events_delegates_to_calendar_client():
    service = Mock()

    with patch.object(calendar_mcp_server, "get_calendar_service", return_value=service), patch.object(
        calendar_mcp_server, "list_upcoming_events", return_value=[{"summary": "Planning"}]
    ) as list_events:
        result = calendar_mcp_server.upcoming_events(5, "work")

    assert result == [{"summary": "Planning"}]
    list_events.assert_called_once_with(service, 5, "work")


def test_add_event_delegates_to_calendar_client():
    service = Mock()
    event = {"summary": "Planning"}

    with patch.object(calendar_mcp_server, "get_calendar_service", return_value=service), patch.object(
        calendar_mcp_server, "get_idempotency_store", return_value=Mock(get=Mock(return_value=None), put=Mock())
    ), patch.object(
        calendar_mcp_server, "create_event", return_value={"id": "event-1"}
    ) as create:
        result = calendar_mcp_server.add_event(event, "work", True, "request-1")

    assert result == {"id": "event-1"}
    create.assert_called_once_with(service, event, "work")


def test_add_event_requires_confirmation():
    with pytest.raises(ValueError, match="confirmation"):
        calendar_mcp_server.add_event({"summary": "Planning"}, "work")


def test_get_calendar_service_caches_authenticated_service(monkeypatch):
    calendar_mcp_server._service = None
    credentials = object()
    service = object()

    with patch.object(calendar_mcp_server, "run_oauth_flow", return_value=credentials) as oauth, patch(
        "src.calendar_client.build_calendar_service", return_value=service
    ) as build:
        first = calendar_mcp_server.get_calendar_service()
        second = calendar_mcp_server.get_calendar_service()

    assert first is service
    assert second is service
    oauth.assert_called_once()
    build.assert_called_once_with(credentials)
    calendar_mcp_server._service = None