# Data Flow

This document details how requests are processed and data flows through the My Agent system.

## Request Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant LangGraph as LangGraph Router
    participant Gemini as Gemini Client
    participant Calendar as Calendar Client
    participant GoogleAPI as Google Calendar API

    User->>LangGraph: Natural language request (e.g. "What's on my calendar?")
    LangGraph->>Gemini: Analyze intent & extract parameters
    Gemini-->>LangGraph: Intent classification (Read/Write/General)
    
    alt General Query
        LangGraph->>Gemini: Generate text response
        Gemini-->>LangGraph: Response text
    else Calendar Read
        LangGraph->>Calendar: list_events()
        Calendar->>GoogleAPI: HTTP GET /calendar/v3/calendars/primary/events
        GoogleAPI-->>Calendar: Event list JSON
        Calendar-->>LangGraph: Formatted events
        LangGraph->>Gemini: Summarize events for user
        Gemini-->>LangGraph: Summary text
    else Calendar Write (Requires Confirmation)
        LangGraph->>User: Request confirmation
        User-->>LangGraph: Confirm / Decline
        opt Confirmed
            LangGraph->>Calendar: create_event()
            Calendar->>GoogleAPI: HTTP POST /calendar/v3/calendars/primary/events
            GoogleAPI-->>Calendar: Created event JSON
            Calendar-->>LangGraph: Success confirmation
        end
    end

    LangGraph-->>User: Final Assistant Response
```

## State Management
- Conversation state and context are tracked via LangGraph nodes.
- OAuth tokens (`token.json`) are securely loaded locally per session.
