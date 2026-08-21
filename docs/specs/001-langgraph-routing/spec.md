# Feature Specification: LangGraph Intent Routing

**Feature Branch**: `001-langgraph-routing`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: Create a LangGraph orchestration layer that decides whether an interaction requires Google Calendar access.

## User Scenarios & Testing

### User Story 1 - Respond without external tools (Priority: P1)

As the user, I want general questions answered without accessing my calendar.

**Why this priority**: It protects privacy and avoids unnecessary API calls.

**Independent Test**: Invoke the graph with a general question and assert that no Calendar tool is called.

**Acceptance Scenarios**:

1. **Given** a general question, **When** the graph processes it, **Then** it returns a response without calling Calendar or Tasks.
2. **Given** a Gemini routing failure, **When** the graph cannot classify the request, **Then** it asks for clarification without performing a mutation.

### User Story 2 - Read calendar information (Priority: P1)

As the user, I want calendar questions routed to the Calendar read tool.

**Why this priority**: Calendar access is the current core capability.

**Independent Test**: Invoke the graph with an availability request and assert the read tool receives the request exactly once.

**Acceptance Scenarios**:

1. **Given** a request about upcoming events, **When** the graph routes it, **Then** it calls the Calendar read operation and summarizes the result.
2. **Given** a Calendar API failure, **When** the read operation fails, **Then** the graph returns a sanitized error response.

### User Story 3 - Confirm calendar mutations (Priority: P1)

As the user, I want event creation to require explicit confirmation.

**Why this priority**: Calendar writes affect personal data and must remain consent-gated.

**Independent Test**: Invoke an event-creation request and assert the graph pauses before calling the write tool.

**Acceptance Scenarios**:

1. **Given** an event request, **When** the event body is prepared, **Then** the graph asks for confirmation before creating it.
2. **Given** a negative confirmation, **When** the user declines, **Then** no Calendar mutation occurs.

### Edge Cases

- Empty input must be rejected without external calls.
- Ambiguous intent must result in clarification.
- A repeated confirmation must not create duplicate events.
- Tool exceptions must not expose credentials, raw prompts or raw API payloads.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST represent conversation state with a typed graph state.
- **FR-002**: The system MUST route direct responses without calling external tools.
- **FR-003**: The system MUST route Calendar reads separately from Calendar writes.
- **FR-004**: The system MUST pause for explicit confirmation before Calendar mutations.
- **FR-005**: The system MUST support cancellation and sanitized error states.
- **FR-006**: The system MUST allow tool dependencies to be injected for unit tests.
- **FR-007**: The system MUST prevent duplicate mutations for a repeated request.

### Key Entities

- **ConversationState**: User input, intent, response, pending action, confirmation and error state.
- **ToolRequest**: The selected operation and its validated arguments.
- **Approval**: Explicit user decision for a pending mutation.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of direct-response test cases execute zero external tools.
- **SC-002**: 100% of mutation test cases require approval before a write call.
- **SC-003**: All graph transitions pass without network access or real credentials.
- **SC-004**: No unit test exposes a secret or raw external payload in an exception.

## Assumptions

- Existing Calendar and Gemini clients remain the integration boundary.
- The initial interface remains the local Python entry point.
- Google Tasks is a future graph tool and is out of scope for this feature.