"""Integration tests for full graph workflow - verifies SC-003."""

from unittest.mock import patch

import pytest

from src.graph.builder import build_graph
from src.graph.nodes.confirmation import clear_execution_history
from src.graph.state import ConversationState, Intent
from src.graph.tools import MockCalendarReadTool, MockCalendarWriteTool


@pytest.fixture
def mock_tools():
    """Provide mock tools for testing without network access."""
    read_tool = MockCalendarReadTool(
        [
            {
                "summary": "Team Standup",
                "start": {"dateTime": "2026-08-25T09:00:00-03:00"},
            },
            {
                "summary": "Client Call",
                "start": {"dateTime": "2026-08-25T14:00:00-03:00"},
            },
        ]
    )
    write_tool = MockCalendarWriteTool()
    return read_tool, write_tool


def test_general_question_no_calendar_access(mock_tools, monkeypatch):
    """
    Verify User Story 1: General questions answered without Calendar.
    Satisfies SC-001 and SC-003.
    """
    read_tool, write_tool = mock_tools

    # Mock all external calls
    monkeypatch.setattr(
        "src.graph.nodes.router.generate_text",
        lambda _: '{"intent": "general"}',
    )
    monkeypatch.setattr(
        "src.graph.nodes.direct.generate_text",
        lambda _: "Paris is the capital of France.",
    )

    graph = build_graph(read_tool, write_tool)
    state: ConversationState = {"user_input": "What is the capital of France?"}

    result = graph.invoke(state)

    # Should return response without calling Calendar
    assert result["response"] == "Paris is the capital of France."
    assert read_tool.call_count == 0
    assert write_tool.call_count == 0


def test_calendar_read_flow(mock_tools, monkeypatch):
    """
    Verify User Story 2: Calendar read requests route to read tool.
    Satisfies SC-003.
    """
    read_tool, write_tool = mock_tools

    monkeypatch.setattr(
        "src.graph.nodes.router.generate_text",
        lambda _: '{"intent": "calendar_read"}',
    )
    monkeypatch.setattr(
        "src.graph.nodes.calendar_read.generate_text",
        lambda _: "You have 2 events: Team Standup at 9am and Client Call at 2pm.",
    )

    graph = build_graph(read_tool, write_tool)
    state: ConversationState = {"user_input": "What's on my calendar tomorrow?"}

    result = graph.invoke(state)

    # Should call read tool exactly once
    assert read_tool.call_count == 1
    assert write_tool.call_count == 0
    assert "Team Standup" in result["response"]


def test_calendar_write_requires_confirmation(mock_tools, monkeypatch):
    """
    Verify User Story 3: Event creation requires confirmation.
    Satisfies SC-002 and SC-003.
    """
    clear_execution_history()
    read_tool, write_tool = mock_tools

    parsed_event = {
        "summary": "Strategy Session",
        "date": "2026-08-26",
        "start_time": "15:00",
        "duration_minutes": 90,
        "timezone": "America/Sao_Paulo",
        "attendees": [],
    }

    monkeypatch.setattr(
        "src.graph.nodes.router.generate_text",
        lambda _: '{"intent": "calendar_write"}',
    )
    monkeypatch.setattr(
        "src.graph.nodes.calendar_write.parse_event_request",
        lambda _: parsed_event,
    )

    graph = build_graph(read_tool, write_tool)

    # First invocation - prepare event
    state: ConversationState = {
        "user_input": "Schedule strategy session tomorrow at 3pm for 90 minutes"
    }
    result = graph.invoke(state)

    # Should prepare but NOT execute
    assert write_tool.call_count == 0
    assert "confirm" in result["response"].lower()
    assert "Strategy Session" in result["response"]

    # Simulate user approval
    result["confirmation"] = True
    result = graph.invoke(result)

    # Now should execute
    assert write_tool.call_count == 1
    assert "created successfully" in result["response"].lower()


def test_declined_confirmation_no_mutation(mock_tools, monkeypatch):
    """
    Verify User Story 3, Scenario 2: Declined confirmation prevents mutation.
    Satisfies SC-002.
    """
    clear_execution_history()
    read_tool, write_tool = mock_tools

    parsed_event = {
        "summary": "Declined Event",
        "date": "2026-08-26",
        "start_time": "10:00",
        "duration_minutes": 30,
        "timezone": "America/Sao_Paulo",
        "attendees": [],
    }

    monkeypatch.setattr(
        "src.graph.nodes.router.generate_text",
        lambda _: '{"intent": "calendar_write"}',
    )
    monkeypatch.setattr(
        "src.graph.nodes.calendar_write.parse_event_request",
        lambda _: parsed_event,
    )

    graph = build_graph(read_tool, write_tool)

    # Prepare event
    state: ConversationState = {"user_input": "Create an event tomorrow at 10am"}
    result = graph.invoke(state)

    # Decline confirmation
    result["confirmation"] = False
    result = graph.invoke(result)

    # No Calendar mutation should occur
    assert write_tool.call_count == 0
    assert "cancelled" in result["response"].lower()


def test_empty_input_rejected(mock_tools):
    """Verify edge case: Empty input rejected without external calls."""
    read_tool, write_tool = mock_tools

    graph = build_graph(read_tool, write_tool)
    state: ConversationState = {"user_input": "   "}

    result = graph.invoke(state)

    assert result["intent"] == Intent.ERROR
    assert "Empty input" in result.get("error", "")
    assert read_tool.call_count == 0
    assert write_tool.call_count == 0


def test_ambiguous_intent_asks_for_clarification(mock_tools, monkeypatch):
    """Verify edge case: Ambiguous intent results in clarification."""
    read_tool, write_tool = mock_tools

    monkeypatch.setattr(
        "src.graph.nodes.router.generate_text",
        lambda _: '{"intent": "clarify"}',
    )

    graph = build_graph(read_tool, write_tool)
    state: ConversationState = {"user_input": "Help me with my thing"}

    result = graph.invoke(state)

    assert "not sure what you're asking" in result["response"].lower()
    assert read_tool.call_count == 0
    assert write_tool.call_count == 0


def test_calendar_api_failure_returns_sanitized_error(mock_tools, monkeypatch):
    """
    Verify User Story 2, Scenario 2: API failure returns sanitized error.
    Satisfies SC-004.
    """

    class FailingReadTool:
        call_count = 0

        def list_events(self, max_results=10, calendar_id="primary"):
            self.call_count += 1
            raise RuntimeError("Internal error: token=abc123")

    read_tool = FailingReadTool()
    write_tool = mock_tools[1]

    monkeypatch.setattr(
        "src.graph.nodes.router.generate_text",
        lambda _: '{"intent": "calendar_read"}',
    )

    graph = build_graph(read_tool, write_tool)
    state: ConversationState = {"user_input": "Show my calendar"}

    result = graph.invoke(state)

    assert result["intent"] == Intent.ERROR
    # Should not expose internal token
    assert "abc123" not in result.get("error", "")
    assert "token=" not in result.get("error", "")


def test_all_transitions_pass_without_network(mock_tools, monkeypatch):
    """
    Verify SC-003: All graph transitions pass without network access.
    
    This test exercises all major paths through the graph using only mocks.
    """
    read_tool, write_tool = mock_tools

    # Test data for each path
    test_cases = [
        {
            "name": "general",
            "user_input": "What is 2+2?",
            "router_response": '{"intent": "general"}',
            "expected_intent": Intent.GENERAL,
        },
        {
            "name": "calendar_read",
            "user_input": "Check my schedule",
            "router_response": '{"intent": "calendar_read"}',
            "expected_intent": Intent.CALENDAR_READ,
        },
        {
            "name": "clarify",
            "user_input": "Help",
            "router_response": '{"intent": "clarify"}',
            "expected_intent": Intent.CLARIFY,
        },
    ]

    for case in test_cases:
        # Reset mock call counts
        read_tool.call_count = 0
        write_tool.call_count = 0

        monkeypatch.setattr(
            "src.graph.nodes.router.generate_text",
            lambda _: case["router_response"],
        )
        monkeypatch.setattr(
            "src.graph.nodes.direct.generate_text",
            lambda _: "Mock response",
        )
        monkeypatch.setattr(
            "src.graph.nodes.calendar_read.generate_text",
            lambda _: "Mock calendar summary",
        )

        graph = build_graph(read_tool, write_tool)
        state: ConversationState = {"user_input": case["user_input"]}

        # Should not raise any exceptions
        result = graph.invoke(state)

        assert result is not None
        assert "response" in result or "error" in result
