"""MCP server exposing the Google Calendar client functions."""
from __future__ import annotations

import os
from typing import Any

from mcp.server.mcpserver import MCPServer

from src.calendar_client import create_event, list_upcoming_events
from src.oauth_flow import run_oauth_flow


mcp = MCPServer("google-calendar")
_service: Any | None = None


def get_calendar_service() -> Any:
    """Create the authenticated Calendar service only when a tool is called."""
    global _service
    if _service is None:
        client_file = os.environ.get("CLIENT_SECRETS_FILE", "credentials.json")
        token_file = os.environ.get("TOKEN_FILE", "token.json")
        credentials = run_oauth_flow(client_file, token_file)

        from src.calendar_client import build_calendar_service

        _service = build_calendar_service(credentials)
    return _service


@mcp.tool()
def upcoming_events(max_results: int = 10, calendar_id: str = "primary") -> list[dict[str, Any]]:
    """List upcoming events from a Google Calendar."""
    return list_upcoming_events(get_calendar_service(), max_results, calendar_id)


@mcp.tool()
def add_event(event_body: dict[str, Any], calendar_id: str = "primary") -> dict[str, Any]:
    """Create a Google Calendar event after the caller confirms the details."""
    return create_event(get_calendar_service(), event_body, calendar_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")