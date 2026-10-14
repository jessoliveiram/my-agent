# Feature Specification: Controlled Cloud Deployment

**Feature Branch**: `006-cloud-deployment`

**Created**: 2026-08-21

**Status**: Draft

**Origin**: Renumbered from `005-cloud-deployment`.

**Input**: Run the Agent Server and required MCP services continuously in a controlled cloud environment.

## User Scenarios & Testing

### User Story 1 - Receive Telegram webhooks reliably (Priority: P1)

The deployed Agent Server receives authenticated HTTPS webhooks and processes them idempotently.

### User Story 2 - Recover state after restart (Priority: P1)

Pending confirmations, workflow sessions and idempotency records survive restart.

### User Story 3 - Operate and recover the service (Priority: P2)

The owner has health checks, logs, backup and rollback procedures.

## Requirements

- Production webhooks MUST use HTTPS and validate a configured secret.
- Pending actions, sessions and idempotency state MUST be durably persisted.
- Production secrets MUST come from a secret manager or deployment secrets.
- Agent and MCP services MUST expose health/readiness checks as appropriate.
- Logs and metrics MUST be structured and sanitized.
- Backup, restore and rollback procedures MUST be documented and tested.
- Credentials MUST NOT be exposed in logs, images or error responses.
- SQLite MUST use durable storage or be replaced by a managed database before multi-worker scale.

## Success Criteria

- Invalid webhook requests cause zero tool calls.
- Restart tests produce zero duplicate mutations.
- Health checks identify unavailable dependencies.
- Recovery restores service state.
- Deployment can roll back to a known-good release.

## Dependencies

- `001-langgraph-mcp-routing`
- `002-calendar-mcp-foundation`
- `003-preferences-drive-sync`
- `004-google-tasks`
- `005-telegram`
- Durable storage and secret-management decision

## Open Questions

- Cloud provider, region and budget.
- Managed database versus durable SQLite volume.
- Whether Agent Server and MCP Server are deployed together or independently.
