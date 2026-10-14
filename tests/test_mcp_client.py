from unittest.mock import AsyncMock, patch

import pytest

from src.mcp_client.client import McpClient, McpClientError, McpToolError


class FakeTool:
    def __init__(self, name: str):
        self.name = name

    def model_dump(self, mode="json"):
        return {"name": self.name, "inputSchema": {"type": "object"}}


class FakeResult:
    isError = False
    structuredContent = {"items": [{"summary": "Planning"}]}
    content = []


class FakeSession:
    def __init__(self):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def initialize(self):
        return None

    async def list_tools(self):
        return type("ListResult", (), {"tools": [FakeTool("list_events")]})()

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return FakeResult()


@pytest.fixture
def client():
    return McpClient(server=object())


def test_list_tools_returns_json_compatible_definitions(client):
    session = FakeSession()

    with patch.object(client, "_session", return_value=session):
        assert client.list_tools() == [
            {"name": "list_events", "inputSchema": {"type": "object"}}
        ]


def test_call_tool_returns_structured_content(client):
    session = FakeSession()

    with patch.object(client, "_session", return_value=session):
        result = client.call_tool("list_events", {"calendar_id": "primary"})

    assert result == {"items": [{"summary": "Planning"}]}
    assert session.calls == [("list_events", {"calendar_id": "primary"})]


def test_call_tool_rejects_mcp_error(client):
    session = FakeSession()

    class ErrorResult:
        isError = True
        structuredContent = None
        content = []

    session.call_tool = AsyncMock(return_value=ErrorResult())

    with patch.object(client, "_session", return_value=session):
        with pytest.raises(McpToolError, match="MCP tool failed"):
            client.call_tool("create_event", {})


def test_client_rejects_active_event_loop(client):
    async def invoke():
        with pytest.raises(McpClientError, match="active event loop"):
            client.list_tools()

    import asyncio

    asyncio.run(invoke())
