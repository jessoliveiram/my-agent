# Feature Specification: Google Tasks Integration

**Feature Branch**: `003-google-tasks`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: Manage Google Tasks and optionally create Calendar events from tasks.

## User Scenarios & Testing

### User Story 1 - Manage task lists and tasks (Priority: P1)

As the user, I want to list, create, update and complete tasks using natural language.

**Why this priority**: Tasks are the next productivity capability after Calendar.

**Independent Test**: Mock the Tasks API and verify each operation and its validated arguments.

**Acceptance Scenarios**:

1. **Given** an authorized Tasks account, **When** the user asks for pending tasks, **Then** the agent returns the relevant list.
2. **Given** a request to create or complete a task, **When** confirmation is denied, **Then** no mutation occurs.

### User Story 2 - Convert a task into a calendar event (Priority: P2)

As the user, I want a selected task with a date and time to become a Calendar event.

**Why this priority**: It connects task planning with the existing calendar workflow.

**Independent Test**: Mock both APIs, confirm the action and verify one linked event is created.

**Acceptance Scenarios**:

1. **Given** a task with a due date and time, **When** the user confirms conversion, **Then** one Calendar event is created.
2. **Given** a task without enough scheduling information, **When** conversion is requested, **Then** the agent asks for the missing information.

### Edge Cases

- Tasks API returns 404, 429, 500 or timeout.
- Pagination returns multiple pages.
- A repeated conversion request must not create duplicate events.
- A task due date has no time or timezone.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST list task lists and pending tasks.
- **FR-002**: The system MUST support task creation, update and completion.
- **FR-003**: The system MUST require confirmation before task mutations.
- **FR-004**: The system MUST require confirmation before creating a Calendar event from a task.
- **FR-005**: The system MUST preserve stable task and event identifiers for deduplication.
- **FR-006**: The system MUST handle pagination and transient API failures.
- **FR-007**: The system MUST use the least-privilege OAuth scope required for Tasks.

### Key Entities

- **Task**: External task identifier, list identifier, title, notes, due date and completion state.
- **TaskEventLink**: Task identifier, event identifier, creation timestamp and idempotency key.
- **TaskMutation**: Pending operation requiring user approval.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All CRUD operation tests pass with mocked API responses.
- **SC-002**: 100% of mutation tests verify confirmation before the API call.
- **SC-003**: Repeated conversion tests create zero duplicate events.
- **SC-004**: 404, 429, 500 and timeout tests return controlled sanitized errors.

## Assumptions

- Google Tasks uses the existing OAuth flow with explicitly reviewed additional scopes.
- Calendar remains the source of truth for scheduled events.
- Natural-language parsing remains delegated to the existing Gemini boundary.