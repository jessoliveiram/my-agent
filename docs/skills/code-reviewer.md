# Skill: `code-reviewer`

## Objective
Analyze Python source code for logical bugs, security vulnerabilities, anti-patterns, concurrency and timezone issues, and readability problems.

## Evaluation Criteria
- **Bugs & Logic:** `None` handling, index/key errors, timezone manipulation, and resource cleanup.
- **Security:** Input sanitization and no exposure of API keys or OAuth tokens in logs or errors.
- **Architecture:** Clear responsibilities, low coupling, and minimal duplication.
- **Maintainability:** Clear naming, static typing, and no dead code.

## Required Output Format
- Review Summary
- Findings & Opportunities (`[Critical/Medium/Low] [File:Line]`)
- Proposed Code / Patch
- Suggested Validation

## Constraints
- Never execute commands that expose `token.json`, `credentials.json`, or `.env`.
- Do not perform large structural refactorings without explicit request.
- Do not reveal credentials or valid third-party tokens.