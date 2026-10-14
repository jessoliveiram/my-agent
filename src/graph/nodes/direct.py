"""Direct response node for general queries without external tools."""

from src.gemini_client import generate_text
from src.graph.state import ConversationState, Intent


def direct_response(state: ConversationState) -> ConversationState:
    """
    Handle general queries without calling external tools.
    
    Satisfies SC-001: Must execute zero external tool calls.
    """
    user_input = state.get("user_input", "")

    try:
        # Generate direct response using Gemini
        response = generate_text(user_input)
        state["response"] = response

    except Exception as e:
        # Sanitize error - no raw exceptions to user
        state["intent"] = Intent.ERROR
        state["error"] = "I encountered an error generating a response. Please try again."

    return state
