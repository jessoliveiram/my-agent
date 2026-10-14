"""Environment-backed application configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass

import dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings shared by the Agent and MCP Server entry points."""

    client_secrets_file: str = "credentials.json"
    token_file: str = "token.json"
    google_api_key: str | None = None
    mcp_server_url: str | None = None
    mcp_transport: str = "stdio"
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000
    mcp_path: str = "/mcp"
    idempotency_db: str = "mcp_idempotency.sqlite3"

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings after applying values from the local .env file."""
        dotenv.load_dotenv()
        return cls(
            client_secrets_file=os.environ.get(
                "CLIENT_SECRETS_FILE", "credentials.json"
            ),
            token_file=os.environ.get("TOKEN_FILE", "token.json"),
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            mcp_server_url=os.environ.get("MCP_SERVER_URL"),
            mcp_transport=os.environ.get("MCP_TRANSPORT", "stdio"),
            mcp_host=os.environ.get("MCP_HOST", "0.0.0.0"),
            mcp_port=int(os.environ.get("MCP_PORT", "8000")),
            mcp_path=os.environ.get("MCP_PATH", "/mcp"),
            idempotency_db=os.environ.get(
                "MCP_IDEMPOTENCY_DB", "mcp_idempotency.sqlite3"
            ),
        )
