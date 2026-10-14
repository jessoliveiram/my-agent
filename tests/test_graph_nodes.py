"""Tests for graph nodes - verifies SC-001, SC-002, SC-004."""

from unittest.mock import Mock, patch

import pytest

from src.graph.nodes.calendar_read import calendar_read
from src.graph.nodes.calendar_write import calendar_write_prepare
from src.graph.nodes.confirmation import clear_execution_history, confirmation
from src.graph.nodes.direct import direct_response
from src.graph.nodes.error import clarify, handle_error
from src.graph.state import ConversationState, Intent, ToolRequest
from src.graph.tools import MockCalendarReadTool, MockCalendarWriteTool


# SC-001: Direct responses must call zero external tools
def test_direct_response_calls_no_external_tools(monkeypatch):
    """
    Verify SC-001: Direct response executes zero external tool calls.
    
    This test uses a mock that tracks calls to ensure no Calendar
    tools are invoked for general questions.
    """
    mock_response = "Paris is the capital of France."
    monkeypatch.setattr(
        "src.graph.nodes.direct.generate_text", lambda _: mock_response
    )

    # Create mock tools that track calls
    read_tool = MockCalendarReadTool()
    write_tool = MockCalendarWriteTool()

    state: ConversationState = {"user_input": "What is the capital of France?"}
    result = direct_response(state)

    assert result["response"] == mock_response
    # Verify zero tool calls
    assert read_tool.call_count == 0
    assert write_tool.call_count == 0


def test_direct_response_handles_error_without_exposing_raw_exception(monkeypatch):
    """Verify SC-004: Direct response errors are sanitized."""

    def mock_generate_error(_):
        raise RuntimeError("Internal API key: sk-secret-12345")

    monkeypatch.setattr("src.graph.nodes.direct.generate_text", mock_generate_error)

    state: ConversationState = {"user_input": "Hello"}
    result = direct_response(state)

    # Error should be sanitized - no raw exception message
    assert "sk-secret-12345" not in result.get("error", "")
    assert "API key" not in result.get("error", "")
    assert result["intent"] == Intent.ERROR


def test_calendar_read_calls_tool_and_summarizes(monkeypatch):
    """Calendar read should call read tool exactly once."""
    mock_events = [
        {"summary": "Meeting", "start": {"dateTime": "2026-08-24T10:00:00-03:00"}}
    ]
    read_tool = MockCalendarReadTool(mock_events)

    mock_summary = "You have a meeting at 10am."
    monkeypatch.setattr(
        "src.graph.nodes.calendar_read.generate_text", lambda _: mock_summary
    )

    state: ConversationState = {"user_input": "What's on my calendar?"}
    result = calendar_read(state, read_tool)

    assert read_tool.call_count == 1
    assert result["response"] == mock_summary
    assert result["tool_result"] == mock_events


def test_calendar_read_handles_empty_calendar(monkeypatch):
    """Calendar read with no events should return appropriate message."""
    read_tool = MockCalendarReadTool([])

    state: ConversationState = {"user_input": "What's on my calendar?"}
    result = calendar_read(state, read_tool)

    assert "no upcoming events" in result["response"].lower()


def test_calendar_read_sanitizes_api_errors():
    """Verify SC-004: Calendar read errors are sanitized."""

    class FailingReadTool:
        def list_events(self, max_results=10, calendar_id="primary"):
            raise RuntimeError("Auth token: ya29.secret-token-xyz")

    read_tool = FailingReadTool()
    state: ConversationState = {"user_input": "Check my calendar"}
    result = calendar_read(state, read_tool)

    assert result["intent"] == Intent.ERROR
    # Should not expose the raw token
    assert "ya29.secret-token-xyz" not in result.get("error", "")
    assert "Auth token" not in result.get("error", "")


# SC-002: Mutations require approval before write call
def test_calendar_write_prepares_without_executing(monkeypatch):
    """
    Verify SC-002: Calendar write prepares action but does NOT execute.
    
    Write tool should have zero calls after calendar_write_prepare.
    """
    parsed_event = {
        "summary": "Team Meeting",
        "date": "2026-08-25",
        "start_time": "15:00",
        "duration_minutes": 60,
        "timezone": "America/Sao_Paulo",
        "attendees": [],
    }
    monkeypatch.setattr(
        "src.graph.nodes.calendar_write.parse_event_request", lambda _: parsed_event
    )

    write_tool = MockCalendarWriteTool()
    state: ConversationState = {"user_input": "Schedule meeting at 3pm tomorrow"}
    result = calendar_write_prepare(state)

    # Should prepare action but NOT execute
    assert result.get("pending_action") is not None
    assert result["pending_action"].operation == "create_event"
    assert "Team Meeting" in result["response"]
    assert "confirm" in result["response"].lower()

    # Verify zero write calls (SC-002)
    assert write_tool.call_count == 0


def test_confirmation_executes_only_after_approval():
    """
    Verify SC-002: Write only executes after explicit approval.
    """
    clear_execution_history()
    write_tool = MockCalendarWriteTool()

    event_body = {
        "summary": "Approved Event",
        "start": {"dateTime": "2026-08-25T15:00:00-03:00"},
    }
    pending = ToolRequest(operation="create_event", arguments={"event_body": event_body})

    # Test approval
    state: ConversationState = {
        "pending_action": pending,
        "confirmation": True,
    }
    result = confirmation(state, write_tool)

    assert write_tool.call_count == 1
    assert "created successfully" in result["response"].lower()
    assert result.get("pending_action") is None


def test_confirmation_cancels_on_decline():
    """Declined confirmation should not execute write."""
    clear_execution_history()
    write_tool = MockCalendarWriteTool()

    event_body = {"summary": "Declined Event"}
    pending = ToolRequest(operation="create_event", arguments={"event_body": event_body})

    state: ConversationState = {
        "pending_action": pending,
        "confirmation": False,
    }
    result = confirmation(state, write_tool)

    assert write_tool.call_count == 0
    assert "cancelled" in result["response"].lower()


def test_confirmation_prevents_duplicate_mutations():
    """Verify FR-007: Repeated request should not create duplicates."""
    clear_execution_history()
    write_tool = MockCalendarWriteTool()

    event_body = {
        "summary": "Unique Event",
        "start": {"dateTime": "2026-08-25T10:00:00-03:00"},
    }
    pending = ToolRequest(operation="create_event", arguments={"event_body": event_body})

    # First execution
    state1: ConversationState = {"pending_action": pending, "confirmation": True}
    result1 = confirmation(state1, write_tool)
    assert write_tool.call_count == 1

    # Second execution with same event
    state2: ConversationState = {"pending_action": pending, "confirmation": True}
    result2 = confirmation(state2, write_tool)

    # Should not create duplicate
    assert write_tool.call_count == 1  # Still 1, not 2
    assert "already created" in result2["response"].lower()


def test_confirmation_sanitizes_write_errors():
    """Verify SC-004: Write errors are sanitized."""
    clear_execution_history()

    class FailingWriteTool:
        def create_event(self, event_body, calendar_id="primary"):
            raise RuntimeError("Database connection string: postgres://user:pass@host")

    write_tool = FailingWriteTool()
    event_body = {"summary": "Test"}
    pending = ToolRequest(operation="create_event", arguments={"event_body": event_body})

    state: ConversationState = {"pending_action": pending, "confirmation": True}
    result = confirmation(state, write_tool)

    assert result["intent"] == Intent.ERROR
    # Should not expose connection string
    assert "postgres://" not in result.get("error", "")
    assert "pass@host" not in result.get("error", "")


def test_error_node_sanitizes_error_messages():
    """Error node should display sanitized error."""
    state: ConversationState = {"error": "Invalid event format"}
    result = handle_error(state)

    assert "❌" in result["response"]
    assert "Invalid event format" in result["response"]


def test_error_node_handles_missing_error():
    """Error node should have fallback for missing error message."""
    state: ConversationState = {}
    result = handle_error(state)

    assert "❌" in result["response"]
    assert "unexpected error" in result["response"].lower()


def test_clarify_node_provides_guidance():
    """Clarify node should help user understand options."""
    state: ConversationState = {}
    result = clarify(state)

    response = result["response"]
    assert "general question" in response.lower()
    assert "calendar" in response.lower()
    assert "event" in response.lower()
