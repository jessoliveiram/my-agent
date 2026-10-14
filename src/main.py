"""Main entry point with LangGraph intent routing."""
from __future__ import annotations

import logging

from google import genai

from src.config import Settings
from src.calendar_client import build_calendar_service
from src.graph import run_graph
from src.graph.tools import McpCalendarReadTool, McpCalendarWriteTool
from src.mcp_client import McpClient


logger = logging.getLogger(__name__)


def main() -> None:
    """Interactive loop using LangGraph intent routing."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )
    settings = Settings.from_env()

    if settings.mcp_server_url:
        mcp_client = McpClient(url=settings.mcp_server_url)
        read_tool = McpCalendarReadTool(mcp_client)
        write_tool = McpCalendarWriteTool(mcp_client)
        calendar_service = None
    else:
        # Local fallback while the MCP server is not configured.
        from src.oauth_flow import run_oauth_flow

        creds = run_oauth_flow(
            settings.client_secrets_file,
            settings.token_file,
        )
        calendar_service = build_calendar_service(creds)
        read_tool = None
        write_tool = None

    print('\n🤖 My Agent - LangGraph Intent Router')
    print('=' * 50)
    print('Ask me anything! I can:')
    print('- Answer general questions')
    print('- Check your calendar')
    print('- Create calendar events (with confirmation)')
    print('\nType "quit" or "exit" to stop.\n')

    # Interactive loop
    while True:
        try:
            user_input = input('You: ').strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print('\nGoodbye! 👋')
                break

            if not user_input:
                continue

            # Run graph with user input
            response = run_graph(
                user_input,
                calendar_service,
                read_tool=read_tool,
                write_tool=write_tool,
            )
            print(f'\nAssistant: {response}\n')

        except KeyboardInterrupt:
            print('\n\nGoodbye! 👋')
            break
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            print(f'\n❌ An error occurred: {type(e).__name__}\n')


def get_available_models() -> None:
    """List available Gemini models that support content generation."""
    api_key = Settings.from_env().google_api_key
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
