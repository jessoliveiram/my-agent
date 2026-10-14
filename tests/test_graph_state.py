"""Tests for graph state definitions."""

import pytest

from src.graph.state import ConversationState, Intent, ToolRequest


def test_intent_enum_values():
    """Verify Intent enum has all required values."""
    assert Intent.GENERAL.value == "general"
    assert Intent.CALENDAR_READ.value == "calendar_read"
    assert Intent.CALENDAR_WRITE.value == "calendar_write"
    assert Intent.CLARIFY.value == "clarify"
    assert Intent.ERROR.value == "error"


def test_tool_request_dataclass():
    """Verify ToolRequest can store operation and arguments."""
    request = ToolRequest(operation="create_event", arguments={"summary": "Meeting"})
    assert request.operation == "create_event"
    assert request.arguments["summary"] == "Meeting"


def test_conversation_state_structure():
    """Verify ConversationState can hold all required fields."""
    state: ConversationState = {
        "user_input": "What's on my calendar?",
        "intent": Intent.CALENDAR_READ,
        "response": "You have 3 events today",
        "pending_action": None,
        "confirmation": None,
        "error": None,
        "tool_result": [],
    }

    assert state["user_input"] == "What's on my calendar?"
    assert state["intent"] == Intent.CALENDAR_READ
    assert state["response"] == "You have 3 events today"
    assert state["pending_action"] is None
