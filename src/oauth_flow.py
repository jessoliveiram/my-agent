"""Perform OAuth installed-app flow and save credentials to a token file.
This follows the Google Calendar Python quickstart pattern.
"""
import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar']


def run_oauth_flow(client_secrets_file: str, token_path: str):
    creds = None
    token_file = Path(token_path)

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    print(f"Saved credentials to {token_path}")
    return creds


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv()
    client_file = os.environ.get('CLIENT_SECRETS_FILE', 'credentials.json')
    token_file = os.environ.get('TOKEN_FILE', 'token.json')
    run_oauth_flow(client_file, token_file)
