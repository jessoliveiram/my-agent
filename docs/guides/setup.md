# Setup Guide

This guide expands on the quick start instructions to help you fully configure and run My Agent.

## Prerequisites

- Python 3.10 or higher installed.
- A Google Cloud project with billing enabled.

## Step-by-Step Installation

1. **Clone and Setup Virtual Environment**:
   ```powershell
   python -m venv venv
   venv\Scripts\Activate
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure Google Cloud Credentials**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the **Google Calendar API** and **Generative AI API**.
   - Create OAuth 2.0 Client IDs (Desktop application) and download the JSON file as `credentials.json` in the root directory.

4. **Environment Variables**:
   - Copy `.env.example` to `.env`:
     ```powershell
     cp .env.example .env
     ```
   - Set `CLIENT_SECRETS_FILE=credentials.json` and your `GOOGLE_API_KEY`.

5. **Authenticate**:
   - Run the OAuth flow script to generate `token.json`:
     ```powershell
   venv\Scripts\python.exe -m src.oauth_flow
     ```

6. **Run Tests**:
   ```powershell
   venv\Scripts\python.exe -m pytest -q
   ```
