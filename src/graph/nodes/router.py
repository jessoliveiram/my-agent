"""Router node for intent classification."""

import json

from src.gemini_client import generate_text
from src.graph.state import ConversationState, Intent


def route(state: ConversationState) -> ConversationState:
    """
    Classify user intent and route to appropriate handler.
    
    Returns updated state with classified intent.
    """
    user_input = state.get("user_input", "").strip()

    # Handle empty input
    if not user_input:
        state["intent"] = Intent.ERROR
        state["error"] = "Empty input received. Please provide a question or request."
        return state

    # Build classification prompt
    prompt = f"""Classify the user's intent for the following request.

User request: {user_input}

Return ONLY a JSON object with a single "intent" field. Valid values:
- "general": General questions that don't require external tools (facts, calculations, explanations)
- "calendar_read": Reading calendar information (checking schedule, listing events, availability)
- "calendar_write": Creating, updating, or deleting calendar events
- "clarify": Ambiguous request that needs clarification

Examples:
{{"intent": "general"}} for "What's the capital of France?"
{{"intent": "calendar_read"}} for "What's on my calendar tomorrow?"
{{"intent": "calendar_write"}} for "Schedule a meeting at 3pm tomorrow"
{{"intent": "clarify"}} for "Help me with my thing"

Response (JSON only):"""

    try:
        response = generate_text(prompt)
        parsed = json.loads(response)
        intent_str = parsed.get("intent", "").lower()

        # Map to Intent enum
        intent_map = {
            "general": Intent.GENERAL,
            "calendar_read": Intent.CALENDAR_READ,
            "calendar_write": Intent.CALENDAR_WRITE,
            "clarify": Intent.CLARIFY,
        }

        if intent_str in intent_map:
            state["intent"] = intent_map[intent_str]
        else:
            # Unknown intent - ask for clarification
            state["intent"] = Intent.CLARIFY

    except (json.JSONDecodeError, KeyError, Exception) as e:
        # Classification failed - ask for clarification
        state["intent"] = Intent.CLARIFY
        state["error"] = f"Could not classify intent. Please rephrase your request."

    return state


def route_condition(state: ConversationState) -> str:
    """
    Determine next node based on classified intent.
    
    Returns node name as string for conditional edge routing.
    """
    intent = state.get("intent")

    if intent == Intent.GENERAL:
        return "direct"
    elif intent == Intent.CALENDAR_READ:
        return "calendar_read"
    elif intent == Intent.CALENDAR_WRITE:
        return "calendar_write"
    elif intent == Intent.CLARIFY:
        return "clarify"
    elif intent == Intent.ERROR:
        return "error"
    else:
        # Fallback to clarify for unknown states
        return "clarify"
