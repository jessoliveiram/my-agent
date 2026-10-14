"""Confirmation node for executing approved mutations."""

from src.graph.state import ConversationState, Intent
from src.graph.tools import CalendarWriteTool


# Track executed actions to prevent duplicates (FR-007)
_executed_actions: set[str] = set()


def confirmation(
    state: ConversationState, write_tool: CalendarWriteTool
) -> ConversationState:
    """
    Execute pending action if approved, or cancel if declined.
    
    Satisfies FR-004: Explicit confirmation before calendar mutations.
    Satisfies FR-007: Prevents duplicate mutations for repeated requests.
    Satisfies SC-002: 100% of mutations require approval before write call.
    
    Args:
        state: Current conversation state with confirmation decision
        write_tool: Injected calendar write tool (for testability)
    
    Returns:
        Updated state with execution result or cancellation message
    """
    confirmation_status = state.get("confirmation")
    pending_action = state.get("pending_action")

    # No pending action - nothing to do
    if not pending_action:
        state["response"] = "No pending action to confirm."
        return state

    # Declined confirmation
    if confirmation_status is False:
        state["pending_action"] = None
        state["response"] = "Event creation cancelled."
        return state

    # Not yet confirmed - preserve existing response from calendar_write
    if confirmation_status is None:
        # Don't overwrite the response if it already exists
        if not state.get("response"):
            state["response"] = "Awaiting confirmation..."
        return state

    # Approved - execute the mutation
    try:
        # Idempotency check (FR-007)
        event_body = pending_action.arguments.get("event_body", {})
        action_key = f"{event_body.get('summary')}_{event_body.get('start')}"

        if action_key in _executed_actions:
            state["response"] = "This event was already created. No duplicate created."
            return state

        # Execute the write operation
        if pending_action.operation == "create_event":
            result = write_tool.create_event(event_body)
            state["tool_result"] = result

            # Mark as executed
            _executed_actions.add(action_key)

            # Success response
            event_link = result.get("htmlLink", "")
            state["response"] = (
                f"✅ Event created successfully!\n\n"
                f"{event_link if event_link else 'Check your calendar for details.'}"
            )
        else:
            state["intent"] = Intent.ERROR
            state["error"] = f"Unknown operation: {pending_action.operation}"

        # Clear pending action
        state["pending_action"] = None

    except Exception as e:
        # Sanitize error per FR-005 and SC-004
        state["intent"] = Intent.ERROR
        state["error"] = "I encountered an error creating the event. Please try again."
        state["pending_action"] = None

    return state


def clear_execution_history():
    """Clear the executed actions set (for testing)."""
    global _executed_actions
    _executed_actions.clear()
