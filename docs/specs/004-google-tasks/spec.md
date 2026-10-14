# Feature Specification: Google Tasks Integration

**Feature Branch**: `004-google-tasks`

**Created**: 2026-08-21

**Status**: Draft

**Origin**: Renumbered from `003-google-tasks`.

**Input**: Manage Google Tasks and optionally create Calendar events from tasks.

## User Scenarios & Testing

### User Story 1 - Manage tasks (Priority: P1)

As the user, I want to list, create, update and complete tasks using natural language.

### User Story 2 - Convert a task into a Calendar event (Priority: P2)

As the user, I want a selected task with a date and time to become a Calendar event.

## Requirements

- The MCP Server MUST expose task-list and pending-task reads.
- The MCP Server MUST support task creation, update and completion.
- Task mutations MUST require explicit confirmation.
- Task-to-event conversion MUST require explicit confirmation.
- Stable task/event identifiers and idempotency keys MUST prevent duplicates.
- Pagination and transient API failures MUST be handled.
- OAuth MUST use the least-privilege Tasks scope.
- Calendar creation MUST use the `002-calendar-mcp-foundation` contract rather than a direct Agent Server API call.

## Edge Cases

- Tasks API returns 404, 429, 500 or timeout.
- Pagination returns multiple pages.
- Repeated conversion request.
- Due date without time or timezone.

## Success Criteria

- CRUD tests pass with mocked API responses.
- Every mutation test verifies confirmation before the API call.
- Repeated conversions create no duplicate events.
- External failures return controlled sanitized errors.

## Dependencies

- `001-langgraph-mcp-routing`
- `002-calendar-mcp-foundation`
- Google Tasks OAuth scope review
