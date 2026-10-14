"""Graph state definitions for conversation tracking and tool coordination."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, TypedDict


class Intent(Enum):
    """User intent classification for routing decisions."""

    GENERAL = "general"
    CALENDAR_READ = "calendar_read"
    CALENDAR_WRITE = "calendar_write"
    CLARIFY = "clarify"
    ERROR = "error"


@dataclass
class ToolRequest:
    """Represents a validated tool operation with its arguments."""

    operation: str
    arguments: dict[str, Any]


class ConversationState(TypedDict, total=False):
    """
    Tracks conversation state across graph nodes.
    
    Fields:
        user_input: Original user message
        intent: Classified intent from router
        response: Final response text to user
        pending_action: Tool request awaiting confirmation
        confirmation: User approval decision (True/False/None)
        error: Sanitized error message if any
        tool_result: Raw result from tool execution
    """

    user_input: str
    intent: Intent
    response: str
    pending_action: ToolRequest | None
    confirmation: bool | None
    error: str | None
    tool_result: Any
