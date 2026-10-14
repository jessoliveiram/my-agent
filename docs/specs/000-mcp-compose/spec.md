# Feature Specification: MCP Compose Architecture Baseline

**Feature Branch**: `000-mcp-compose`

**Created**: 2026-10-14

**Status**: Done

**Origin**: Renamed from `000-refactor-mcp-compose`; records the refactor baseline implemented before the numbered roadmap was realigned.

## Purpose

Define the operational architecture for running the Agent Server and Calendar
MCP Server as separate Docker Compose services, with clear ownership of the
MCP Client boundary and an optional diagnostic client.

This specification records the baseline already delivered. It does not add a
new productivity domain or claim production-ready remote authentication.

## Responsibilities

### Agent Server

The Agent Server owns the user-facing application, LangGraph routing,
conversation state and confirmation flow. It contains the MCP Client as a
Python library and does not need a separate MCP Client container for normal
operation.

### MCP Client Library

The MCP Client library owns MCP session initialization, tool discovery,
tool invocation, transport handling and result normalization. It does not own
Google OAuth, Calendar business rules or Google API credentials.

### MCP Server

The MCP Server owns the Calendar MCP tools, Google OAuth, Google Calendar API
integration, validation, mutation confirmation and idempotency storage. It can
run with `stdio` for local hosts or Streamable HTTP for Compose.

### Diagnostic Client

`mcp-client-tools` is an optional diagnostic process used to verify MCP
connectivity and discover published tools. It is not a production hop and is
not required for the Agent Server to operate.

## Runtime Topology

Normal application flow:

```text
User -> Agent Server -> MCP Client library -> MCP Server -> Google Calendar API
```

Optional diagnostic flow:

```text
mcp-client-tools -> MCP Server
```

## Docker Compose Baseline

The Compose deployment MUST keep the following services independently
buildable and runnable:

- `agent`: interactive Agent Server with the embedded MCP Client library.
- `mcp-server`: Calendar MCP Server using Streamable HTTP.
- `mcp-client-tools`: optional discovery CLI enabled by the `tools` profile.

The Compose baseline MUST provide:

- an internal service URL through `MCP_SERVER_URL`;
- `mcp-server` healthcheck and Agent dependency on server readiness;
- `mcp-server-data` volume for SQLite idempotency state;
- external configuration for `GOOGLE_API_KEY`, OAuth paths and MCP settings;
- no credentials copied into Docker images;
- separate Dockerfiles and commands for each runtime;
- `stdio` support outside Compose for local MCP hosts.

Relevant configuration includes `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`,
`MCP_PATH`, `MCP_IDEMPOTENCY_DB`, `MCP_SERVER_URL`, `CLIENT_SECRETS_FILE`
and `TOKEN_FILE`.

## Delivered Baseline

- Agent Server, MCP Client and MCP Server responsibilities are separated.
- MCP Client supports `stdio` and Streamable HTTP.
- Calendar adapters allow the graph to use MCP without changing graph nodes.
- Dockerfiles and `compose.yaml` define independent runtimes.
- Runtime configuration is centralized in `src/config.py`.
- Calendar mutations require confirmation and an idempotency key.
- Completed mutation results are persisted in SQLite.
- Tests cover MCP discovery, invocation, adapters and persistence.

## Scope Boundaries

This baseline does not complete:

- remote MCP authentication and authorization;
- multi-agent identity and audit records;
- atomic reservation for concurrent idempotency requests;
- persistent Agent workflow sessions and pending approvals;
- final versioned Calendar tool names;
- cloud deployment and rollback.

Those concerns belong to later roadmap specifications.

## Acceptance Evidence

- Python test suite passes.
- MCP Server and diagnostic client complete local Streamable HTTP discovery.
- `docker compose config` succeeds.
- Each runtime has an independent Dockerfile and command.
- Docker image build depends on an available Docker daemon.
