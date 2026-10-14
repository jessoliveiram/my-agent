# Feature Specification: Calendar MCP Foundation

**Feature Branch**: `002-calendar-mcp-foundation`

**Created**: 2026-10-14

**Status**: Partial

**Origin**: Extracted from the former `006-shared-productivity-mcp` as its local/fundational scope.

**Input**: Provide a stable Calendar MCP boundary for the Agent Server and future productivity capabilities.

## User Stories

### User Story 1 - Discover Calendar tools

As an MCP Client, I want stable Calendar tool names and machine-readable schemas so that the Agent Server does not call Google APIs directly.

### User Story 2 - Protect Calendar mutations

As the user, I want Calendar writes to require confirmation and remain idempotent across retries and restarts.

### User Story 3 - Run locally and in Compose

As a developer, I want the same Calendar MCP implementation to run over `stdio` locally and Streamable HTTP in Compose.

## Requirements

- The server MUST publish stable read and write tool contracts.
- The server MUST validate tool arguments before calling Google Calendar.
- Read and mutation operations MUST remain separate.
- Mutations MUST require explicit confirmation and an idempotency key.
- Idempotency reservation and completion MUST be atomic for concurrent requests.
- Completed results MUST survive process restarts.
- Errors MUST be sanitized and must not expose credentials or private payloads.
- Local and HTTP transports MUST execute the same contract tests.
- OAuth credentials MUST remain inside the MCP Server boundary.
- The Agent Server MUST consume Calendar through MCP adapters.

## Proposed Initial Contract

- `list_calendar_events`
- `create_calendar_event`

The existing `upcoming_events` and `add_event` names are compatibility aliases until the final contract is adopted.

## Acceptance Criteria

- A client discovers the documented tools and schemas.
- A read request reaches Google Calendar exactly once.
- A write without confirmation performs zero external writes.
- A confirmed retry with the same key performs one external write.
- Concurrent requests with the same key perform one external write.
- The same scenarios pass over `stdio` and Streamable HTTP.

## Out of Scope

- Multi-tenant remote authorization.
- Telegram sessions.
- Google Tasks.
- Cloud deployment and rollback.

## Dependencies

- `001-langgraph-mcp-routing`
- Google Calendar OAuth and domain client
- MCP Python SDK
