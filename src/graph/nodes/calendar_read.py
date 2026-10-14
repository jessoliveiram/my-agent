"""Calendar read node for retrieving and summarizing events."""

from src.gemini_client import generate_text
from src.graph.state import ConversationState, Intent
from src.graph.tools import CalendarReadTool


def calendar_read(
    state: ConversationState, read_tool: CalendarReadTool
) -> ConversationState:
    """
    Retrieve calendar events and summarize for the user.
    
    Args:
        state: Current conversation state
        read_tool: Injected calendar read tool (for testability)
    
    Returns:
        Updated state with response or sanitized error
    """
    user_input = state.get("user_input", "")

    try:
        # Call calendar read tool
        events = read_tool.list_events(max_results=10)
        state["tool_result"] = events

        # Build summary prompt
        if not events:
            state["response"] = "You have no upcoming events on your calendar."
        else:
            # Format events for summarization
            events_text = "\n".join(
                [
                    f"- {event.get('summary', 'Untitled')} at {event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'No time'))}"
                    for event in events
                ]
            )

            prompt = f"""The user asked: {user_input}

Here are their upcoming calendar events:
{events_text}

Provide a natural, helpful response summarizing the relevant information."""

            response = generate_text(prompt)
            state["response"] = response

    except Exception as e:
        # Sanitize error per FR-005 and SC-004
        state["intent"] = Intent.ERROR
        state["error"] = (
            "I encountered an error accessing your calendar. Please try again later."
        )

    return state
