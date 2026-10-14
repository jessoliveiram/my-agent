"""MCP client diagnostics entry point."""
from __future__ import annotations

from src.config import Settings
from src.mcp_client import McpClient


def main() -> None:
    url = Settings.from_env().mcp_server_url or "http://mcp-server:8000/mcp"
    client = McpClient(url=url)
    for tool in client.list_tools():
        print(tool.get("name", "<unnamed>"))


if __name__ == "__main__":
    main()
