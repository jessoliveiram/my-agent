# Data Flow

This document details how requests are processed and data flows through the My Agent system.

## Request Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant Agent as Agent Server
    participant MCPClient as MCP Client
    participant Gemini as Gemini Client
    participant MCPServer as MCP Server
    participant Calendar as Calendar Integration
    participant GoogleAPI as Google Calendar API

    User->>Agent: Natural language request (e.g. "What's on my calendar?")
    Agent->>Gemini: Analyze intent & extract parameters
    Gemini-->>Agent: Intent classification (Read/Write/General)
    
    alt General Query
        Agent->>Gemini: Generate text response
        Gemini-->>Agent: Response text
    else Calendar Read
        Agent->>MCPClient: list_tools / call_tool
        MCPClient->>MCPServer: list_events()
        MCPServer->>Calendar: HTTP GET /calendar/v3/calendars/primary/events
        GoogleAPI-->>Calendar: Event list JSON
        Calendar-->>MCPServer: Formatted events
        MCPServer-->>MCPClient: Tool result
        MCPClient-->>Agent: Formatted events
        Agent->>Gemini: Summarize events for user
        Gemini-->>Agent: Summary text
    else Calendar Write (Requires Confirmation)
        Agent->>User: Request confirmation
        User-->>Agent: Confirm / Decline
        opt Confirmed
            Agent->>MCPClient: create_event()
            MCPClient->>MCPServer: create_event()
            MCPServer->>Calendar: HTTP POST /calendar/v3/calendars/primary/events
            GoogleAPI-->>Calendar: Created event JSON
            Calendar-->>MCPServer: Success confirmation
            MCPServer-->>MCPClient: Tool result
            MCPClient-->>Agent: Success confirmation
        end
    end

    Agent-->>User: Final Assistant Response
```

## State Management
- Conversation state and context are tracked via LangGraph nodes.
- OAuth tokens (`token.json`) are loaded by the MCP Server and are never passed
    through the Agent Server or MCP Client.
