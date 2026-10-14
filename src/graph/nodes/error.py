"""Error handling node for sanitized error responses."""

from src.graph.state import ConversationState


def handle_error(state: ConversationState) -> ConversationState:
    """
    Generate user-friendly error message from error state.
    
    Satisfies FR-005: Sanitized error states.
    Satisfies SC-004: No secrets or raw payloads exposed.
    
    Returns:
        Updated state with sanitized error response
    """
    error_msg = state.get("error")

    if error_msg:
        # Error already sanitized in previous node
        state["response"] = f"❌ {error_msg}"
    else:
        # Generic fallback
        state["response"] = (
            "❌ An unexpected error occurred. Please try again or rephrase your request."
        )

    return state


def clarify(state: ConversationState) -> ConversationState:
    """
    Request clarification for ambiguous input.
    
    Returns:
        Updated state with clarification request
    """
    state["response"] = (
        "I'm not sure what you're asking. Could you please:\n\n"
        "- Ask a general question (e.g., 'What's the weather?')\n"
        "- Check your calendar (e.g., 'What's on my schedule?')\n"
        "- Create an event (e.g., 'Schedule a meeting at 3pm tomorrow')"
    )

    return state
