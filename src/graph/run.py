"""Entry point for running the LangGraph intent routing workflow."""

from typing import Any

from src.graph.builder import build_graph
from src.graph.state import ConversationState
from src.graph.tools import (
    CalendarReadTool,
    CalendarWriteTool,
    DefaultCalendarReadTool,
    DefaultCalendarWriteTool,
)


def run_graph(
    user_input: str,
    calendar_service: Any | None = None,
    *,
    read_tool: CalendarReadTool | None = None,
    write_tool: CalendarWriteTool | None = None,
) -> str:
    """
    Execute the graph workflow with user input.
    
    Args:
        user_input: User's natural language request
        calendar_service: Authenticated Google Calendar service, retained for
            local fallback compatibility
        read_tool: Optional injected calendar read tool
        write_tool: Optional injected calendar write tool
    
    Returns:
        Final response text to display to user
    """
    if read_tool is None or write_tool is None:
        if calendar_service is None:
            raise ValueError("calendar_service or both calendar tools are required")
        read_tool = DefaultCalendarReadTool(calendar_service)
        write_tool = DefaultCalendarWriteTool(calendar_service)

    # Build and compile graph
    graph = build_graph(read_tool, write_tool)

    # Initialize state
    initial_state: ConversationState = {
        "user_input": user_input,
    }

    # Execute graph
    try:
        result = graph.invoke(initial_state)

        # Handle confirmation interrupt
        if result.get("pending_action") and result.get("confirmation") is None:
            # Event prepared, waiting for user confirmation
            confirmation_msg = result.get("response", "Please confirm.")
            print(f"\n{confirmation_msg}")

            # Get user confirmation
            user_choice = input("\nConfirm? (yes/no): ").strip().lower()
            result["confirmation"] = user_choice in ["yes", "y"]

            # Re-invoke to execute confirmation node
            result = graph.invoke(result)

        return result.get("response", "No response generated.")

    except Exception as e:
        # Final safety net - sanitize any unhandled errors
        return f"❌ An unexpected error occurred: {type(e).__name__}. Please try again."
