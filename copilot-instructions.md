# Copilot / Assistant Instructions (workspace)

## Purpose
- Assist in developing this agent that integrates Google Calendar and Gemini.

## Context
- This repository contains an integration example with Google Calendar and Gemini (Generative AI).
- Skills are documented in `docs/skills/`, and external connections are configured in `docs/mcp/mcp.json`.

## Workflow
- Make small, testable changes.
- Always run local tests before creating larger changes: `pytest -q`.
- Use a Python virtual environment (`venv`) and install dependencies with `pip install -r requirements.txt`.
- Refer to `README.md`, `docs/`, `docs/skills/`, and `docs/mcp/mcp.json` to understand the project purpose, workflows, skills, and integrations.

## Important Rules
- NEVER add keys, credentials, or `credentials.json` to the repository.
- If credentials are needed, instruct the user to add them to `.env` and document the environment variable names.
- Prefer isolated changes; explain reasons and trade-offs concisely.

## Style and Quality
- Suggest and apply small refactorings that improve readability and testability.
- When proposing automated changes, always include a quick test plan (commands to run).
- Keep code consistent with best practices for Python and used frameworks.
- Follow naming and style conventions of the project.

## Testing and Execution
- Activate venv (PowerShell):
```powershell
venv\Scripts\Activate
pip install -r requirements.txt
pytest -q
```
- Run the app (example):
```powershell
python -m src.main
```

If more context is needed, ask for: 1) file(s) to modify, 2) short objective (1-2 sentences), 3) test requirements.
