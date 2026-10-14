"""Calendar write node for preparing event creation requests."""

from src.event_creator import build_event_body, parse_event_request
from src.graph.state import ConversationState, Intent, ToolRequest


def calendar_write_prepare(state: ConversationState) -> ConversationState:
    """
    Parse event request and prepare for confirmation.
    
    Does NOT execute the write - stores pending_action for confirmation node.
    Satisfies FR-004: Must pause for explicit confirmation.
    
    Returns:
        Updated state with pending_action or sanitized error
    """
    user_input = state.get("user_input", "")

    try:
        # Parse natural language event request
        parsed_event = parse_event_request(user_input)

        # Build validated event body
        event_body = build_event_body(parsed_event)

        # Store as pending action (do NOT execute yet)
        state["pending_action"] = ToolRequest(
            operation="create_event", arguments={"event_body": event_body}
        )

        # Build confirmation message
        summary = event_body.get("summary", "Untitled event")
        start_time = (
            event_body.get("start", {}).get("dateTime")
            or event_body.get("start", {}).get("date")
            or "unspecified time"
        )

        state["response"] = (
            f"I'll create the following event:\n\n"
            f"**{summary}**\n"
            f"Start: {start_time}\n\n"
            f"Please confirm to proceed."
        )

    except ValueError as e:
        # Validation error - sanitized message
        state["intent"] = Intent.ERROR
        state["error"] = f"Invalid event details: {str(e)}"
    except Exception as e:
        # Generic error - sanitized per FR-005 and SC-004
        state["intent"] = Intent.ERROR
        state["error"] = "I couldn't parse the event details. Please try rephrasing your request."

    return state
