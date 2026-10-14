# Technology Stack

This document outlines the core technologies used in My Agent and the rationale behind their selection.

## Core Technologies

| Technology | Purpose | Rationale |
| :--- | :--- | :--- |
| **Python 3.10+** | Core runtime | Rich ecosystem for AI/ML, robust API client libraries. |
| **Google Generative AI SDK** | Gemini API wrapper | Official SDK for interacting with Gemini models. |
| **Google API Client (`google-api-python-client`)** | Google Calendar API | Standard library for Google Workspace integrations. |
| **LangGraph / LangChain** | Intent routing & orchestration | Robust framework for stateful, multi-actor LLM applications. |
| **MCP Python SDK** | Client/server tool protocol | Connects the Agent Server to the independent Calendar MCP Server. |
| **Docker Compose** | Local service orchestration | Runs the Agent Server, MCP Server, and diagnostic client independently. |
| **pytest** | Unit & integration testing | Industry standard for Python testing with fixture support. |

## Design Principles
- **Modularity**: Separation between Agent Server, MCP Client, MCP Server, and Google integrations.
- **Security-First**: No hardcoded credentials; strict reliance on environment variables and local OAuth token storage.
- **Testability**: Independent unit tests with complete mocking of external network calls.
