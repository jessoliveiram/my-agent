"""Perform OAuth installed-app flow and save credentials to a token file.
This follows the Google Calendar Python quickstart pattern.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError

SCOPES = ['https://www.googleapis.com/auth/calendar']
logger = logging.getLogger(__name__)


def run_oauth_flow(client_secrets_file: str, token_path: str) -> Any:
    """Load, refresh, or obtain OAuth credentials without logging token data."""
    client_file = Path(client_secrets_file)
    if not client_file.is_file():
        raise FileNotFoundError("OAuth client secrets file was not found")

    creds = None
    token_file = Path(token_path)

    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        except (ValueError, OSError) as exc:
            raise RuntimeError("Unable to read OAuth token file") from exc

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as exc:
                raise RuntimeError("Unable to refresh OAuth credentials") from exc
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
            creds = flow.run_local_server(port=0)

        token_file.parent.mkdir(parents=True, exist_ok=True)
        with token_file.open('w', encoding='utf-8') as token:
            token.write(creds.to_json())

    logger.info("OAuth credentials are ready")
    return creds


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv()
    client_file = os.environ.get('CLIENT_SECRETS_FILE', 'credentials.json')
    token_file = os.environ.get('TOKEN_FILE', 'token.json')
    run_oauth_flow(client_file, token_file)
