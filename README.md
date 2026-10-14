# My Agent with Gemini and MCP

The project is split into three runtime responsibilities:

```text
User -> Agent Server -> MCP Client -> MCP Server -> Google Calendar API
```

The Agent Server contains the MCP Client as a Python library. The MCP Server
owns Google Calendar authentication and API calls.

## Quick start

1. Activate venv:

```powershell
venv\Scripts\Activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the unit tests:

```powershell
pytest -q
```

4. Create OAuth client credentials in Google Cloud Console and download the JSON as `credentials.json`.

5. Copy `.env.example` to `.env` and set `CLIENT_SECRETS_FILE`, `TOKEN_FILE`, and `GOOGLE_API_KEY`.

6. Run the OAuth flow to obtain `token.json` for the local fallback:

```powershell
venv\Scripts\python.exe -m src.oauth_flow
```

7. Run the local example:

```powershell
venv\Scripts\python.exe -m src.main
```

Files created:
- `src/mcp_client/` — MCP session, discovery, and tool invocation client.
- `src/graph/tools.py` — direct and MCP-backed Calendar adapters.
- `src/calendar_mcp_server.py` — Calendar MCP Server, supporting `stdio` and Streamable HTTP.
- `src/gemini_client.py` — wrapper to call Gemini (uses `google-generativeai` if available).
- `.env.example` — environment variable template.

## Docker Compose

Build and run the MCP Server, Agent Server, or diagnostic client independently:

```powershell
docker compose build
docker compose up mcp-server
docker compose run --rm mcp-client-tools
docker compose run --rm agent
```

The Agent Server uses `MCP_SERVER_URL` when configured. Without it, the local
direct Calendar API path remains available as a development fallback.

## Documentation

For comprehensive guides, architecture overview, and feature specifications, visit the [Documentation Directory](docs/README.md).

- **Setup Guide**: [Setup Guide](docs/guides/setup.md)
- **Quality Skills**: [Skills directory](docs/skills/)
- **MCP Configuration**: [mcp.json](docs/mcp/mcp.json)

The Calendar MCP server exposes `upcoming_events` and `add_event` to MCP-compatible clients.
`add_event` requires `confirmed=true` and a stable `idempotency_key`; repeated
requests with the same key return the previously created event.

## Agents and Skills

This repository keeps reusable software-engineering skills in `docs/skills/`, separated by responsibility for code review, test review, and test creation.

### Available Skills:

1. **Code Reviewer**
   - **Objective:** Analyze Python source code for logical bugs, security flaws, anti-patterns, concurrency/timezone issues and readability.
   - **Output Format:** Review summary, prioritized findings (critical/medium/low), proposed patch code and suggested validation commands.

2. **Test Auditor**
   - **Objective:** Audit existing test suites (`pytest`, `unittest`) to identify flaky tests, incorrect or excessive mocks, missing assertions and corner-case gaps.
   - **Output Format:** Test suite diagnosis, identified gaps/fragilities, improvement recommendations and execution instructions.

3. **Test Generator**
   - **Objective:** Write robust, execution-ready `pytest` test suites covering happy paths, alternative flows, and controlled failures.
   - **Output Format:** Scope of generated tests, test implementations (`tests/test_<module>.py`) and pytest execution commands.

## Next steps

Development is guided by the GitHub Spec Kit specifications in `docs/specs/`:

1. [MCP Compose baseline](docs/specs/000-mcp-compose/spec.md): record the separated Docker Compose architecture already delivered.
2. [LangGraph MCP routing](docs/specs/001-langgraph-mcp-routing/spec.md): route requests through MCP-compatible Calendar tools.
3. [Calendar MCP foundation](docs/specs/002-calendar-mcp-foundation/spec.md): finalize Calendar contracts and durable idempotency.
4. [Preferences and Google Drive](docs/specs/003-preferences-drive-sync/spec.md): persist preferences locally with backup.
5. [Google Tasks](docs/specs/004-google-tasks/spec.md): manage tasks and convert them into events when necessary.
6. [Telegram](docs/specs/005-telegram/spec.md): add a remote conversational interface.
7. [Cloud deployment](docs/specs/006-cloud-deployment/spec.md): continuous operation of the system.
8. [Shared remote MCP](docs/specs/007-shared-productivity-mcp/spec.md): authenticated multi-agent productivity service.
