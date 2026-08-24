# Skill: `test-reviewer`

## Objective
Audit existing pytest suites for flaky tests, incorrect mocks, weak assertions, isolation problems, and missing edge cases.

## Evaluation Criteria
- Verify mocks match external API contracts without mocking the code under test.
- Detect dependencies on live credentials, network access, environment state, or test order.
- Check empty responses, timeouts, HTTP errors, malformed payloads, and timezone boundaries.
- Prefer clear Arrange, Act, Assert structure and meaningful assertions.

## Required Output Format
- Test Suite Diagnosis
- Identified Gaps & Fragilities
- Improvement Recommendations
- Execution Instructions with pytest