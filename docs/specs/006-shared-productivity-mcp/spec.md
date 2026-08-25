# Feature Specification: Shared Productivity MCP Server

**Feature Branch**: `006-shared-productivity-mcp`

**Created**: 2026-08-24

**Status**: Future

**Input**: User description: Expose Calendar, Tasks and related productivity capabilities through one independently deployable MCP server that can be consumed by multiple agents.

## User Scenarios & Testing

### User Story 1 - Share productivity tools across agents (Priority: P1)

As the owner, I want Telegram, web, CLI and orchestration agents to use the same productivity tools without duplicating Google API integration code.

**Why this priority**: A shared tool boundary is the primary benefit of introducing MCP.

**Independent Test**: Connect two MCP-compatible clients and verify that both can discover and invoke an allowed Calendar tool through the same server.

**Acceptance Scenarios**:

1. **Given** an authorized MCP client, **When** it requests the server capabilities, **Then** it discovers the published productivity tools and their input schemas.
2. **Given** two authorized clients, **When** both request read operations, **Then** both receive results through the shared MCP service.
3. **Given** a client that does not have permission for a tool, **When** it invokes that tool, **Then** the server rejects the request without calling the external API.

### User Story 2 - Require confirmation for mutations (Priority: P1)

As the user, I want creating or changing Calendar and Tasks data to remain explicit and auditable even when requests originate from different agents.

**Why this priority**: A shared server increases the number of callers and therefore the risk of accidental mutations.

**Independent Test**: Submit a mutation without confirmation and verify that no external write occurs; submit the same mutation with valid confirmation and verify one write.

**Acceptance Scenarios**:

1. **Given** a request to create or modify data without confirmation, **When** the MCP tool is called, **Then** it returns a confirmation-required result and performs no mutation.
2. **Given** a confirmed mutation, **When** the request is retried with the same idempotency key, **Then** only one external mutation occurs.
3. **Given** an invalid or expired confirmation, **When** a mutation is requested, **Then** the server rejects it without exposing credentials or private data.

### User Story 3 - Run locally or as a shared service (Priority: P2)

As the owner, I want the same MCP implementation to support local development and a centrally hosted deployment.

**Why this priority**: Local `stdio` is useful for development, while multiple remote agents need a network transport.

**Independent Test**: Start the server with local transport and with the selected authenticated network transport, then run the same tool contract against both modes.

**Acceptance Scenarios**:

1. **Given** a local MCP client, **When** it starts the configured server over `stdio`, **Then** it can discover and invoke the tools.
2. **Given** a remote authorized client, **When** it connects to the hosted endpoint, **Then** it can use the same tool schemas and authorization rules.
3. **Given** an unauthenticated or invalidly authenticated remote client, **When** it connects, **Then** no tool execution or external API call occurs.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST expose Calendar and Tasks capabilities through documented MCP tools.
- **FR-002**: The system MUST publish machine-readable input schemas and stable tool names.
- **FR-003**: The server MUST support local `stdio` transport for development.
- **FR-004**: The production deployment MUST use an authenticated network transport suitable for concurrent agents.
- **FR-005**: Every tool invocation MUST identify the calling client or agent for authorization and audit purposes.
- **FR-006**: Read and mutation permissions MUST be separable by client, agent or user identity.
- **FR-007**: Mutation tools MUST require explicit confirmation and an idempotency key.
- **FR-008**: The server MUST reuse shared domain clients and authentication code instead of duplicating Google API calls in each agent.
- **FR-009**: The server MUST isolate credentials and user data between authorized users or tenants if multi-user access is introduced.
- **FR-010**: The server MUST return controlled, non-sensitive errors for authentication, validation, rate-limit and external API failures.
- **FR-011**: The server MUST expose health, readiness and structured audit information without logging tokens or event contents unnecessarily.
- **FR-012**: The repository layout MUST remain independent from the transport choice; a monorepo MAY be used, but MUST NOT be required for MCP clients to consume the service.

### Key Entities

- **McpClientIdentity**: Agent or application identity, permissions, user association and credential reference.
- **ToolContract**: Stable tool name, description, input schema, output shape and mutation classification.
- **Confirmation**: User-approved action, expiration, target identity and idempotency key.
- **AuditRecord**: Client identity, tool, timestamp, outcome, correlation ID and sanitized error details.
- **ServiceConfig**: Transport, allowed origins, authentication provider, external service settings and limits.

## Suggested Initial Tools

- `list_calendar_events`
- `create_calendar_event`
- `list_tasks`
- `complete_task`

Tool names and payloads are subject to a contract review before implementation. Existing functions in `src/calendar_client.py` should remain the first implementation target for Calendar tools.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Two independent MCP clients discover the same published tool contracts and complete authorized read calls.
- **SC-002**: Unauthorized and insufficiently authorized requests produce zero external API calls.
- **SC-003**: Duplicate mutation requests with the same idempotency key produce exactly one external write.
- **SC-004**: Local `stdio` and production network transport pass the same contract test suite.
- **SC-005**: Audit records identify the client and outcome without containing access tokens or unnecessary private event data.
- **SC-006**: At least one agent can be moved from direct Calendar calls to MCP without changing the shared Calendar domain client.

## Assumptions

- Specifications `001` through `005` establish routing, persistence, Telegram access and deployment foundations before this feature is implemented.
- The first release may remain single-user, but authorization boundaries must not prevent future multi-user support.
- `stdio` is intended for local development and single-client usage; production multi-agent access requires an authenticated network deployment.
- A monorepo is an organizational option, not an architectural dependency. Separate repositories are also valid if the MCP tool contracts are versioned and documented.
- OAuth token storage, refresh behavior and secret management must follow the deployment and security requirements in `005-cloud-deployment`.

## Open Questions

- Which authenticated MCP network transport and hosting model will be supported first?
- Will all agents act on one Google account, or will the server support multiple user accounts in the first release?
- Where will confirmations and idempotency records be persisted for concurrent requests?
- Should authorization be based on agent identity, end-user identity, or both?
- What versioning policy applies when a tool schema changes?
