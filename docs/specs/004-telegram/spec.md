# Feature Specification: Telegram Bot Interface

**Feature Branch**: `004-telegram`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: Offer the My-Agent through Telegram as a conversational interface.

## User Scenarios & Testing

### User Story 1 - Converse through Telegram (Priority: P1)

As the user, I want to send natural-language messages through Telegram and receive My-Agent responses.

**Why this priority**: Telegram provides a convenient remote interface while remaining independent from deployment decisions.

**Independent Test**: Mock Telegram updates and verify they are mapped to the graph and response sent to the correct chat.

**Acceptance Scenarios**:

1. **Given** an authorized Telegram user, **When** a message arrives, **Then** the agent processes it through the same graph as the local interface.
2. **Given** an unauthorized user, **When** a message arrives, **Then** no Calendar, Tasks or preference data is exposed.

### User Story 2 - Confirm actions through Telegram (Priority: P1)

As the user, I want to approve or cancel Calendar and Tasks mutations in the chat.

**Why this priority**: Remote interaction must preserve the existing consent requirement.

**Independent Test**: Mock an approval callback and verify exactly one approved or zero rejected mutations.

**Acceptance Scenarios**:

1. **Given** a pending event creation, **When** the user confirms, **Then** the graph resumes and invokes the write tool once.
2. **Given** a pending mutation, **When** the user cancels, **Then** the graph completes without invoking a write tool.

### Edge Cases

- Duplicate Telegram updates.
- Messages exceeding the supported size.
- User sends a new request while an approval is pending.
- Telegram API timeout or malformed update.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST use `python-telegram-bot` as a transport adapter.
- **FR-002**: The system MUST map Telegram identities to isolated application sessions.
- **FR-003**: The system MUST reuse the LangGraph workflow used by local execution.
- **FR-004**: The system MUST support explicit confirmation and cancellation through Telegram.
- **FR-005**: The system MUST reject unauthorized users before invoking personal-data tools.
- **FR-006**: The system MUST handle duplicate updates idempotently.
- **FR-007**: The system MUST keep Telegram transport concerns separate from domain tools.

### Key Entities

- **TelegramUser**: External Telegram identity and authorization status.
- **ConversationSession**: User-scoped graph state and pending approval.
- **UpdateReceipt**: Telegram update identifier and processing status.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Authorized messages reach the graph in 100% of mocked adapter tests.
- **SC-002**: Unauthorized messages result in zero personal-data tool calls.
- **SC-003**: Duplicate update tests result in zero duplicate mutations.
- **SC-004**: All confirmation tests preserve the existing consent behavior.

## Assumptions

- This feature is implemented only after LangGraph, preferences and Tasks interfaces are stable.
- Polling is acceptable for local development; production transport is specified separately.