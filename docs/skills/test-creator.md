# Skill: `test-creator`

## Objective
Write complete, deterministic, execution-ready pytest suites for happy paths, alternative flows, boundaries, and controlled failures.

## Implementation Guidelines
- Use reusable fixtures in `conftest.py` or the test module.
- Mock external SDKs and network calls with `unittest.mock` or pytest fixtures.
- Use `@pytest.mark.parametrize` for input and boundary variations.
- Follow the Arrange, Act, Assert pattern.

## Required Output Format
- Scope of Generated Tests
- Test Implementation in `tests/test_<module>.py`
- Commands for Execution with pytest