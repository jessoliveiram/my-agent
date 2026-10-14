# Architecture Overview

This document provides a high-level overview of the My Agent system, detailing the components and their interactions.

## System Components

1. **Orchestration Layer (LangGraph)**:
   - Routes user intentions to the appropriate tool or agent.
   - Manages conversation state and decision logic.

2. **Agent Server**:
   - Owns the interactive application and LangGraph workflow.
   - Uses `src/mcp_client` to discover and invoke Calendar tools.

3. **MCP Server**:
   - `src/calendar_mcp_server.py` exposes Calendar tools over `stdio` or Streamable HTTP.
   - Owns OAuth and calls to `src/calendar_client.py`.

4. **Integration Clients**:
   - **Gemini Client (`src/gemini_client.py`)**: Wrapper for Google Generative AI API calls.
   - **Calendar Client (`src/calendar_client.py`)**: Internal integration used by the MCP Server.

3. **Authentication Layer (`src/oauth_flow.py`)**:
   - Handles OAuth2 flow for Google account authorization and persists tokens.

4. **Intelligence Layer**:
   - Google Gemini provides reasoning and natural language processing capabilities.

## High-Level Data Flow

1. **Input**: User provides a prompt.
2. **Routing**: LangGraph analyzes intent to determine if external tools are needed.
3. **Execution**:
   - If general question: Gemini answers directly.
   - If calendar request: Router invokes the MCP-backed Calendar adapter.
5. **Output**: System provides the natural language response.
