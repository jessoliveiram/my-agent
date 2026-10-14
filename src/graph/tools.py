"""Tool protocols and implementations for dependency injection."""

import hashlib
import json
from typing import Any, Protocol

from src import calendar_client
from src.mcp_client import McpClient


class CalendarReadTool(Protocol):
    """Protocol for calendar read operations."""

    def list_events(
        self, max_results: int = 10, calendar_id: str = "primary"
    ) -> list[dict[str, Any]]:
        """List upcoming calendar events."""
        ...


class CalendarWriteTool(Protocol):
    """Protocol for calendar write operations."""

    def create_event(
        self, event_body: dict[str, Any], calendar_id: str = "primary"
    ) -> dict[str, Any]:
        """Create a new calendar event."""
        ...


class DefaultCalendarReadTool:
    """Default implementation wrapping calendar_client for reads."""

    def __init__(self, service: Any):
        self.service = service

    def list_events(
        self, max_results: int = 10, calendar_id: str = "primary"
    ) -> list[dict[str, Any]]:
        """List upcoming calendar events."""
        return calendar_client.list_upcoming_events(
            self.service, max_results=max_results, calendar_id=calendar_id
        )


class DefaultCalendarWriteTool:
    """Default implementation wrapping calendar_client for writes."""

    def __init__(self, service: Any):
        self.service = service

    def create_event(
        self, event_body: dict[str, Any], calendar_id: str = "primary"
    ) -> dict[str, Any]:
        """Create a new calendar event."""
        return calendar_client.create_event(
            self.service, event_body, calendar_id=calendar_id
        )


class McpCalendarReadTool:
    """Calendar read adapter backed by an MCP client."""

    def __init__(self, client: McpClient, tool_name: str = "upcoming_events"):
        self.client = client
        self.tool_name = tool_name

    def list_events(
        self, max_results: int = 10, calendar_id: str = "primary"
    ) -> list[dict[str, Any]]:
        result = self.client.call_tool(
            self.tool_name,
            {"max_results": max_results, "calendar_id": calendar_id},
        )
        if not isinstance(result, list):
            raise RuntimeError("MCP calendar read returned an invalid result")
        return result


class McpCalendarWriteTool:
    """Calendar write adapter backed by an MCP client."""

    def __init__(self, client: McpClient, tool_name: str = "add_event"):
        self.client = client
        self.tool_name = tool_name

    def create_event(
        self, event_body: dict[str, Any], calendar_id: str = "primary"
    ) -> dict[str, Any]:
        idempotency_key = hashlib.sha256(
            json.dumps(
                {"calendar_id": calendar_id, "event_body": event_body},
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        result = self.client.call_tool(
            self.tool_name,
            {
                "event_body": event_body,
                "calendar_id": calendar_id,
                "confirmed": True,
                "idempotency_key": idempotency_key,
            },
        )
        if not isinstance(result, dict):
            raise RuntimeError("MCP calendar write returned an invalid result")
        return result


class MockCalendarReadTool:
    """Mock implementation for testing without network access."""

    def __init__(self, mock_events: list[dict[str, Any]] | None = None):
        self.mock_events = mock_events or []
        self.call_count = 0

    def list_events(
        self, max_results: int = 10, calendar_id: str = "primary"
    ) -> list[dict[str, Any]]:
        """Return mock events."""
        self.call_count += 1
        return self.mock_events[:max_results]


class MockCalendarWriteTool:
    """Mock implementation for testing without network access."""

    def __init__(self):
        self.created_events: list[dict[str, Any]] = []
        self.call_count = 0

    def create_event(
        self, event_body: dict[str, Any], calendar_id: str = "primary"
    ) -> dict[str, Any]:
        """Record event creation without external call."""
        self.call_count += 1
        event = {**event_body, "id": f"mock_event_{self.call_count}"}
        self.created_events.append(event)
        return event
