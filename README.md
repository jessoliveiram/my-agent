# My Agent with Gemini

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

5. Copy `.env.example` to `.env` and set `CLIENT_SECRETS_FILE` and `GOOGLE_API_KEY`.

6. Run the OAuth flow to obtain `token.json`:

```powershell
venv\Scripts\python.exe -m src.oauth_flow
```

7. Run the example:

```powershell
venv\Scripts\python.exe -m src.main
```

Files created:
- `src/oauth_flow.py` — performs OAuth installed app flow and saves `token.json`.
- `src/calendar_client.py` — helper to list/create calendar events.
- `src/gemini_client.py` — wrapper to call Gemini (uses `google-generativeai` if available).
- `.env.example` — environment variable template.

## Documentation

For comprehensive guides, architecture overview, and feature specifications, visit the [Documentation Directory](docs/README.md).

- **Calendar Integration**: [Calendar Integration](docs/guides/calendar-integration.md)
- **Quality Skills**: [Skills directory](docs/skills/)
- **MCP Configuration**: [mcp.json](docs/mcp/mcp.json)

The Calendar MCP server exposes `upcoming_events` and `add_event` to MCP-compatible clients.

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

1. [LangGraph intent routing](docs/specs/001-langgraph-routing/spec.md): decide when and if it is necessary to query or modify the calendar.
2. [SQLite preferences and Google Drive](docs/specs/002-preferences-drive-sync/spec.md): persist preferences locally with backup.
3. [Google Tasks](docs/specs/003-google-tasks/spec.md): manage tasks and convert them into events when necessary.
4. [Telegram](docs/specs/004-telegram/spec.md): add a remote conversational interface.
5. [Cloud deployment](docs/specs/005-cloud-deployment/spec.md): continuous operation of the system.
