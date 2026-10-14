# Development Guide

This guide outlines development practices, coding standards, and testing workflows for contributors.

## Development Workflow

1. **Virtual Environment**: Always activate `venv` before running commands or tests.
2. **Test-Driven Changes**: Run `pytest -q` before and after making changes to ensure no regressions.
3. **Static Analysis**: Follow PEP 8 style guidelines and use type hints (`typing`) across all Python code in `src/`.

## Running Tests

Execute the test suite using pytest:
```powershell
pytest -v
```

All external API calls must be mocked in unit tests (see existing tests in `tests/`).

## MCP Development Flow

Run the MCP Server locally with `MCP_TRANSPORT=stdio` for an MCP host that
launches it as a child process, or with `MCP_TRANSPORT=streamable-http` for
the same network boundary used by Compose. The Agent Server connects through
`MCP_SERVER_URL`; the MCP Client diagnostic command verifies discovery without
executing Calendar mutations.

The Agent Server must not import Google Calendar API code for the MCP path.
Google credentials belong to the MCP Server and must stay outside Docker
images and source control.

Mutation calls must include explicit confirmation and a stable
`idempotency_key`. The MCP Server persists completed results in SQLite so a
retry after a process restart does not create a second event.

## Quality Skills

Use the quality skills in `/skills` during development by prompting Copilot Chat:
- *"Code Reviewer: review `src/event_creator.py` and propose fixes."*
- *"Test Reviewer: audit `tests/test_event_creator.py` for missing cases."*
- *"Test Creator: generate tests for `src/calendar_client.py`."*
