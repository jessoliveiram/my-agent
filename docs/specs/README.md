# Feature Specifications Index

This directory contains the feature specifications for the My Agent development roadmap, following the GitHub Spec Kit methodology.

## 📋 Roadmaps & Features

1. **[000-mcp-compose](000-mcp-compose/spec.md)** — **Done**
   *Baseline MCP Client/Server, Compose and configuration refactor.*

2. **[001-langgraph-mcp-routing](001-langgraph-mcp-routing/spec.md)** — **Done**
   *LangGraph routing over MCP-compatible Calendar adapters.*

3. **[002-calendar-mcp-foundation](002-calendar-mcp-foundation/spec.md)** — **Partial**
   *Stable Calendar MCP contracts, confirmation and idempotency.*

4. **[003-preferences-drive-sync](003-preferences-drive-sync/spec.md)** — **Draft**
   *Local preferences database with Google Drive backup.*

5. **[004-google-tasks](004-google-tasks/spec.md)** — **Draft**
   *Tasks management and task-to-Calendar conversion through MCP.*

6. **[005-telegram](005-telegram/spec.md)** — **Draft**
   *Telegram transport adapter for the Agent Server.*

7. **[006-cloud-deployment](006-cloud-deployment/spec.md)** — **Draft**
   *Continuous operation, recovery and deployment controls.*

8. **[007-shared-productivity-mcp](007-shared-productivity-mcp/spec.md)** — **Future**
   *Authenticated remote MCP service shared by multiple agents.*

## 📐 Spec Kit Methodology
Each specification file is a standalone living document. Supporting artifacts may be added inside its folder as implementation begins:
- `plan.md` (Implementation Planning)
- `research.md` (Spikes/Evaluations)
- `data-model.md` (Database/State schemas)
- `contracts/` (API Schemas)
- `tasks.md` (Task Lists)
