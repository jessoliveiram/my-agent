"""Example runner: obtain creds, list upcoming events, ask Gemini to summarize."""
from __future__ import annotations

import logging
import os

import dotenv
from google import genai

from src.oauth_flow import run_oauth_flow
from src.calendar_client import build_calendar_service, list_upcoming_events
from src.gemini_client import generate_text
from src.event_creator import create_event_from_nl


logger = logging.getLogger(__name__)


def load_env() -> None:
    dotenv.load_dotenv()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )
    load_env()
    client_secrets = os.environ.get('CLIENT_SECRETS_FILE', 'credentials.json')
    token_file = os.environ.get('TOKEN_FILE', 'token.json')

    creds = run_oauth_flow(client_secrets, token_file)
    service = build_calendar_service(creds)

    events = list_upcoming_events(service, max_results=5)
    if not events:
        print('No upcoming events found.')
        return

    summary_prompt = 'Summarize the following calendar events in bullet points:\n'
    for e in events:
        start = e.get('start', {}).get('dateTime', e.get('start', {}).get('date'))
        summary_prompt += f"- {start}: {e.get('summary', 'No title')}\n"

    print('Asking Gemini to summarize events...')
    try:
        summary = generate_text(summary_prompt)
        print('\nGemini summary:\n')
        print(summary)
    except Exception:
        logger.error('Gemini generation failed')

    # Offer to create an event using natural language
    ans = input('\nWould you like to create an event by natural language? (y/N): ').strip().lower()
    if ans == 'y':
        nl = input('Describe the event you want to create (e.g. "Meeting with Ana tomorrow 10am for 30 minutes, invite ana@example.com"):\n')
        create_event_from_nl(service, nl)


def get_available_models() -> None:
    """List available Gemini models that support content generation."""
    load_env()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set GOOGLE_API_KEY in your environment (eg .env or $env:GOOGLE_API_KEY)"
        )

    client = genai.Client(api_key=api_key)
    print("Available models for content generation:")
    for model in client.models.list():
        if "generateContent" in model.supported_actions:
            print(f"- {model.name}")

if __name__ == '__main__':
    main()
