"""Tests for router node intent classification."""

from unittest.mock import patch

import pytest

from src.graph.nodes.router import route, route_condition
from src.graph.state import ConversationState, Intent


def test_route_empty_input_returns_error():
    """Empty input should be rejected without external calls."""
    state: ConversationState = {"user_input": "   "}

    result = route(state)

    assert result["intent"] == Intent.ERROR
    assert "Empty input" in result["error"]


def test_route_classifies_general_question(monkeypatch):
    """General questions should be classified as GENERAL intent."""
    mock_response = '{"intent": "general"}'
    monkeypatch.setattr("src.graph.nodes.router.generate_text", lambda _: mock_response)

    state: ConversationState = {"user_input": "What is the capital of France?"}
    result = route(state)

    assert result["intent"] == Intent.GENERAL


def test_route_classifies_calendar_read(monkeypatch):
    """Calendar read requests should be classified as CALENDAR_READ."""
    mock_response = '{"intent": "calendar_read"}'
    monkeypatch.setattr("src.graph.nodes.router.generate_text", lambda _: mock_response)

    state: ConversationState = {"user_input": "What's on my calendar tomorrow?"}
    result = route(state)

    assert result["intent"] == Intent.CALENDAR_READ


def test_route_classifies_calendar_write(monkeypatch):
    """Event creation requests should be classified as CALENDAR_WRITE."""
    mock_response = '{"intent": "calendar_write"}'
    monkeypatch.setattr("src.graph.nodes.router.generate_text", lambda _: mock_response)

    state: ConversationState = {"user_input": "Schedule a meeting at 3pm tomorrow"}
    result = route(state)

    assert result["intent"] == Intent.CALENDAR_WRITE


def test_route_handles_invalid_json_response(monkeypatch):
    """Malformed Gemini response should result in CLARIFY intent."""
    monkeypatch.setattr("src.graph.nodes.router.generate_text", lambda _: "not json")

    state: ConversationState = {"user_input": "Help me with something"}
    result = route(state)

    assert result["intent"] == Intent.CLARIFY


def test_route_handles_unknown_intent(monkeypatch):
    """Unknown intent value should result in CLARIFY."""
    mock_response = '{"intent": "unknown_value"}'
    monkeypatch.setattr("src.graph.nodes.router.generate_text", lambda _: mock_response)

    state: ConversationState = {"user_input": "Do something"}
    result = route(state)

    assert result["intent"] == Intent.CLARIFY


def test_route_condition_maps_intents_to_nodes():
    """Route condition should map each intent to correct node name."""
    assert route_condition({"intent": Intent.GENERAL}) == "direct"
    assert route_condition({"intent": Intent.CALENDAR_READ}) == "calendar_read"
    assert route_condition({"intent": Intent.CALENDAR_WRITE}) == "calendar_write"
    assert route_condition({"intent": Intent.CLARIFY}) == "clarify"
    assert route_condition({"intent": Intent.ERROR}) == "error"


def test_route_condition_handles_missing_intent():
    """Missing intent should default to clarify."""
    assert route_condition({}) == "clarify"
