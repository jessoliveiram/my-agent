# Feature Specification: Shared Remote Productivity MCP

**Feature Branch**: `007-shared-productivity-mcp`

**Created**: 2026-10-14

**Status**: Future

**Origin**: Remote and multi-agent scope extracted from the former `006-shared-productivity-mcp`.

**Input**: Expose Calendar, Tasks and related productivity tools through an authenticated MCP service consumed by multiple agents.

## User Stories

### User Story 1 - Authorize MCP clients

As the owner, I want every remote MCP caller identified and authorized before personal-data tools execute.

### User Story 2 - Share tools across agents

As an agent owner, I want multiple authorized clients to discover and invoke the same versioned tool contracts.

### User Story 3 - Audit mutations

As the owner, I want confirmed mutations, retries and outcomes auditable without logging tokens or unnecessary private event data.

## Requirements

- The production network transport MUST require authentication.
- Every invocation MUST identify the client, agent and associated user.
- Read and mutation permissions MUST be separable.
- User data and credentials MUST be isolated by authorized identity.
- Mutation confirmation MUST be bound to the caller, user, target and expiration.
- Idempotency MUST remain atomic under concurrent clients.
- Tool schemas MUST be versioned and compatibility rules documented.
- The server MUST expose health, readiness and sanitized audit records.
- Calendar and Tasks tools MUST reuse shared domain integrations.
- Local `stdio` behavior MUST remain covered by the same contract suite.

## Acceptance Criteria

- An unauthorized client receives no tool execution or external API call.
- Two authorized clients discover the same published contracts.
- A client lacking mutation permission is rejected before Google API access.
- An expired or mismatched confirmation is rejected.
- Duplicate concurrent mutations create one external record.
- Audit records identify caller and outcome without secrets or unnecessary event contents.

## Dependencies

- `002-calendar-mcp-foundation`
- `004-google-tasks`
- `006-cloud-deployment`
- Durable identity, session and idempotency storage

## Open Questions

- Which identity provider and MCP authentication mechanism will be used?
- Will the first release support one Google account or multiple users?
- Which transport and hosting model will be operated in production?
- What is the tool schema versioning and deprecation policy?
