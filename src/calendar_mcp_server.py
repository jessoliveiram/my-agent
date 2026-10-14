"""MCP server exposing the Google Calendar client functions."""
from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from src.calendar_client import create_event, list_upcoming_events
from src.config import Settings
from src.idempotency_store import IdempotencyStore
from src.oauth_flow import run_oauth_flow


mcp = MCPServer("google-calendar")
_service: Any | None = None
_idempotency_store: IdempotencyStore | None = None


def get_calendar_service() -> Any:
    """Create the authenticated Calendar service only when a tool is called."""
    global _service
    if _service is None:
        settings = Settings.from_env()
        credentials = run_oauth_flow(
            settings.client_secrets_file,
            settings.token_file,
        )

        from src.calendar_client import build_calendar_service

        _service = build_calendar_service(credentials)
    return _service


def get_idempotency_store() -> IdempotencyStore:
    """Create the persistent mutation store only when a write is requested."""
    global _idempotency_store
    if _idempotency_store is None:
        _idempotency_store = IdempotencyStore(Settings.from_env().idempotency_db)
    return _idempotency_store


@mcp.tool()
def upcoming_events(max_results: int = 10, calendar_id: str = "primary") -> list[dict[str, Any]]:
    """List upcoming events from a Google Calendar."""
    return list_upcoming_events(get_calendar_service(), max_results, calendar_id)


@mcp.tool()
def add_event(
    event_body: dict[str, Any],
    calendar_id: str = "primary",
    confirmed: bool = False,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    """Create an event only after explicit confirmation."""
    if not confirmed:
        raise ValueError("explicit confirmation is required")
    if not idempotency_key:
        raise ValueError("idempotency_key is required")

    store = get_idempotency_store()
    existing = store.get(idempotency_key)
    if existing is not None:
        return existing

    result = create_event(get_calendar_service(), event_body, calendar_id)
    store.put(idempotency_key, result)
    return result


if __name__ == "__main__":
    settings = Settings.from_env()
    transport = settings.mcp_transport
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        mcp.run(
            transport="streamable-http",
            host=settings.mcp_host,
            port=settings.mcp_port,
            streamable_http_path=settings.mcp_path,
        )
    else:
        raise ValueError(f"Unsupported MCP_TRANSPORT: {transport}")