"""Graph builder for assembling the intent routing workflow."""

from functools import partial
from typing import Any

from langgraph.graph import END, StateGraph

from src.graph.nodes import (
    calendar_read,
    calendar_write,
    confirmation,
    direct,
    error,
    router,
)
from src.graph.state import ConversationState
from src.graph.tools import CalendarReadTool, CalendarWriteTool


def build_graph(
    read_tool: CalendarReadTool, write_tool: CalendarWriteTool
) -> StateGraph:
    """
    Build the LangGraph workflow with injected tools.
    
    Graph structure:
        START → router
        router → direct | calendar_read | calendar_write | clarify | error
        calendar_write → confirmation
        confirmation → END
        direct/calendar_read/clarify/error → END
    
    Args:
        read_tool: Calendar read tool implementation (real or mock)
        write_tool: Calendar write tool implementation (real or mock)
    
    Returns:
        Compiled StateGraph ready for invocation
    """
    # Create graph with ConversationState
    graph = StateGraph(ConversationState)

    # Add router as entry point
    graph.add_node("router", router.route)

    # Add handler nodes with tool injection
    graph.add_node("direct", direct.direct_response)
    graph.add_node(
        "calendar_read", partial(calendar_read.calendar_read, read_tool=read_tool)
    )
    graph.add_node("calendar_write", calendar_write.calendar_write_prepare)
    graph.add_node(
        "confirmation", partial(confirmation.confirmation, write_tool=write_tool)
    )
    graph.add_node("error", error.handle_error)
    graph.add_node("clarify", error.clarify)

    # Set entry point
    graph.set_entry_point("router")

    # Add conditional edges from router
    graph.add_conditional_edges(
        "router",
        router.route_condition,
        {
            "direct": "direct",
            "calendar_read": "calendar_read",
            "calendar_write": "calendar_write",
            "clarify": "clarify",
            "error": "error",
        },
    )

    # Calendar write flows to confirmation
    graph.add_edge("calendar_write", "confirmation")

    # Terminal nodes flow to END
    graph.add_edge("direct", END)
    graph.add_edge("calendar_read", END)
    graph.add_edge("confirmation", END)
    graph.add_edge("clarify", END)
    graph.add_edge("error", END)

    return graph.compile()
