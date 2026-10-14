# Deployment Guide

## Local Compose

The repository contains three independently buildable runtime images:

- `agent`: interactive Agent Server;
- `mcp-server`: Calendar MCP Server over Streamable HTTP;
- `mcp-client-tools`: optional MCP discovery and diagnostics command.

Run them with:

```powershell
docker compose build
docker compose up mcp-server
docker compose run --rm mcp-client-tools
docker compose run --rm agent
```

The MCP Server mounts `credentials.json` read-only and `token.json` as a
writable token file. These files are ignored by Git and must never be copied
into a Docker image.

The Compose volume `mcp-server-data` stores the MCP Server idempotency database.
Back up or replace this volume according to the deployment environment; losing
it removes the server's durable duplicate-mutation history.

## Cloud Deployment

Continuous operation and cloud deployment strategies remain detailed in
[spec `006-cloud-deployment`](../specs/006-cloud-deployment/spec.md).

## Overview
Continuous operation and cloud deployment strategies for My Agent. Refer to [docs/specs/006-cloud-deployment/spec.md](../specs/006-cloud-deployment/spec.md) for full architectural requirements.
