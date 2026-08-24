# Feature Specifications Index

This directory contains the feature specifications for the My Agent development roadmap, following the GitHub Spec Kit methodology.

## 📋 Roadmaps & Features

1. **[001-langgraph-routing](001-langgraph-routing/spec.md)**  
   *Intent routing layer using LangGraph to decide if calendar/tasks access is needed.*

2. **[002-preferences-drive-sync](002-preferences-drive-sync/spec.md)**  
   *Local preferences database using SQLite with remote backup sync via Google Drive API.*

3. **[003-google-tasks](003-google-tasks/spec.md)**  
   *Integrate task management and task-to-calendar-event conversion capabilities.*

4. **[004-telegram](004-telegram/spec.md)**  
   *Conversational interface using Telegram Bot API for remote agent interactions.*

5. **[005-cloud-deployment](005-cloud-deployment/spec.md)**  
   *Continuous operation cloud setup.*

## 📐 Spec Kit Methodology
Each specification file operates as a standalone living document. Over time, features evolve inside their respective folders through:
- `plan.md` (Implementation Planning)
- `research.md` (Spikes/Evaluations)
- `data-model.md` (Database/State schemas)
- `contracts/` (API Schemas)
- `tasks.md` (Task Lists)
