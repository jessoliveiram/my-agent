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

## Quality Skills

Use the quality skills in `/skills` during development by prompting Copilot Chat:
- *"Code Reviewer: review `src/event_creator.py` and propose fixes."*
- *"Test Reviewer: audit `tests/test_event_creator.py` for missing cases."*
- *"Test Creator: generate tests for `src/calendar_client.py`."*
