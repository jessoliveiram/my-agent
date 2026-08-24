# Architecture Overview

This document provides a high-level overview of the My Agent system, detailing the components and their interactions.

## System Components

1. **Orchestration Layer (LangGraph)**:
   - Routes user intentions to the appropriate tool or agent.
   - Manages conversation state and decision logic.

2. **Integration Clients**:
   - **Gemini Client (`src/gemini_client.py`)**: Wrapper for Google Generative AI API calls.
   - **Calendar Client (`src/calendar_client.py`)**: Facilitates reading/creating/updating events via Google Calendar API.

3. **Authentication Layer (`src/oauth_flow.py`)**:
   - Handles OAuth2 flow for Google account authorization and persists tokens.

4. **Intelligence Layer**:
   - Google Gemini provides reasoning and natural language processing capabilities.

## High-Level Data Flow

1. **Input**: User provides a prompt.
2. **Routing**: LangGraph analyzes intent to determine if external tools are needed.
3. **Execution**:
   - If general question: Gemini answers directly.
   - If calendar request: Router invokes `calendar_client`.
4. **Output**: System provides the natural language response.
