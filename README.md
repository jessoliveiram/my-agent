# Calendar-Gemini Agent

Quick start

1. Activate venv:

```powershell
venv\Scripts\Activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create OAuth client credentials in Google Cloud Console and download the JSON as `credentials.json`.

4. Copy `.env.example` to `.env` and set `CLIENT_SECRETS_FILE` and `GOOGLE_API_KEY`.

5. Run the OAuth flow to obtain `token.json`:

```powershell
python -m src.oauth_flow
```

6. Run the example:

```powershell
python -m src.main
```

Files created:
- `src/oauth_flow.py` — performs OAuth installed app flow and saves `token.json`.
- `src/calendar_client.py` — helper to list/create calendar events.
- `src/gemini_client.py` — wrapper to call Gemini (uses `google-generativeai` if available).
- `.env.example` — environment variable template.

Code Reviewer
--------------------------------

This repository includes an agent description for a code reviewer in `agent.md`. You can ask the assistant to run that reviewer to inspect files and propose patches.

How to invoke the reviewer (examples):

- In VS Code Copilot Chat, ask:
	- "Revisor de Código: revise `src/event_creator.py` e proponha correções." 
	- "Use the Revisor de Código to audit `src/gemini_client.py` for error handling and tests."


Agent file: `agent.md` — contains the `Revisor de Código` skill definition and invocation examples.
