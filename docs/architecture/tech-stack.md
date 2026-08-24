# Technology Stack

This document outlines the core technologies used in My Agent and the rationale behind their selection.

## Core Technologies

| Technology | Purpose | Rationale |
| :--- | :--- | :--- |
| **Python 3.10+** | Core runtime | Rich ecosystem for AI/ML, robust API client libraries. |
| **Google Generative AI SDK** | Gemini API wrapper | Official SDK for interacting with Gemini models. |
| **Google API Client (`google-api-python-client`)** | Google Calendar API | Standard library for Google Workspace integrations. |
| **LangGraph / LangChain** | Intent routing & orchestration | Robust framework for stateful, multi-actor LLM applications. |
| **pytest** | Unit & integration testing | Industry standard for Python testing with fixture support. |

## Design Principles
- **Modularity**: Separation of concerns between API clients (`src/`), orchestration, and testing (`tests/`).
- **Security-First**: No hardcoded credentials; strict reliance on environment variables and local OAuth token storage.
- **Testability**: Independent unit tests with complete mocking of external network calls.
