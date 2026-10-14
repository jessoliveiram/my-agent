# Feature Specification: LangGraph MCP Intent Routing

**Feature Branch**: `001-langgraph-mcp-routing`

**Created**: 2026-08-21

**Status**: Done

**Origin**: Renumbered and aligned with `000-mcp-compose`.

**Input**: Create a LangGraph orchestration layer that decides whether an interaction requires an MCP Calendar tool.

## User Stories

### User Story 1 - Respond without external tools

General questions MUST be answered without invoking Calendar or Tasks tools.

### User Story 2 - Read Calendar information

Calendar questions MUST be routed to an injected Calendar read tool and summarized.

### User Story 3 - Confirm Calendar mutations

Event creation MUST pause for explicit confirmation before invoking the write tool.

## Requirements

- The system MUST represent conversation state with a typed graph state.
- Direct responses MUST execute zero external tools.
- Calendar reads and writes MUST use separate injected MCP-compatible tools.
- Calendar mutations MUST require explicit confirmation.
- Cancellation and errors MUST be sanitized.
- Tool dependencies MUST be injectable for tests.
- A stable idempotency key MUST be passed to the Calendar MCP boundary for repeated requests.
- The Agent Server MUST NOT require direct Google Calendar API access on the MCP path.

## Edge Cases

- Empty input.
- Ambiguous intent.
- Repeated confirmation.
- Tool exceptions containing credentials or private payloads.

## Success Criteria

- Direct-response tests invoke zero external tools.
- Mutation tests verify approval before writes.
- Graph transitions run without network access or real credentials.
- Errors do not expose secrets or raw external payloads.

## Dependencies

- `000-mcp-compose`
- `002-calendar-mcp-foundation`
- Gemini client boundary

## Out of Scope

Google Tasks implementation, Telegram transport and cloud deployment.
