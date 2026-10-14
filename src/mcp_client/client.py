"""Synchronous facade over the asynchronous MCP Python SDK."""
from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client


class McpClientError(RuntimeError):
    """Base error for MCP connection and protocol failures."""


class McpToolError(McpClientError):
    """Raised when an MCP tool reports an execution error."""


class McpClient:
    """Invoke tools exposed by an MCP server.

    The public methods are synchronous so they can be injected into the existing
    synchronous LangGraph nodes. A session is opened per operation for now;
    session pooling can be added when the Agent Server becomes long-lived.
    """

    def __init__(
        self,
        server: StdioServerParameters | None = None,
        url: str | None = None,
    ):
        if (server is None) == (url is None):
            raise ValueError("Provide exactly one MCP server transport")
        self.server = server
        self.url = url

    def list_tools(self) -> list[dict[str, Any]]:
        """Discover tools and return JSON-compatible definitions."""
        result = self._run(self._list_tools())
        return [self._model_dump(tool) for tool in result.tools]

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Call an MCP tool and return its structured or JSON result."""
        result = self._run(self._call_tool(name, arguments or {}))
        if getattr(result, "isError", False):
            raise McpToolError(f"MCP tool failed: {name}")
        return self._extract_result(result)

    async def _list_tools(self) -> Any:
        async with self._session() as session:
            return await session.list_tools()

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        async with self._session() as session:
            return await session.call_tool(name, arguments)

    @asynccontextmanager
    async def _session(self) -> AsyncIterator[ClientSession]:
        try:
            if self.url:
                streams_context = streamable_http_client(self.url)
            else:
                streams_context = stdio_client(self.server)

            async with streams_context as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()
                    yield session
        except McpClientError:
            raise
        except Exception as exc:
            raise McpClientError("Unable to connect to MCP server") from exc

    @staticmethod
    def _run(coroutine: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coroutine)
        coroutine.close()
        raise McpClientError(
            "Synchronous MCP client cannot run inside an active event loop"
        )

    @staticmethod
    def _model_dump(value: Any) -> dict[str, Any]:
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")
        if hasattr(value, "dict"):
            return value.dict()
        if isinstance(value, dict):
            return value
        raise McpClientError("MCP returned an unsupported tool definition")

    @classmethod
    def _extract_result(cls, result: Any) -> Any:
        structured = getattr(result, "structuredContent", None)
        if structured is not None:
            return structured

        content = getattr(result, "content", None) or []
        values: list[Any] = []
        for item in content:
            text = getattr(item, "text", None)
            if text is None:
                continue
            try:
                values.append(json.loads(text))
            except json.JSONDecodeError:
                values.append(text)

        if len(values) == 1:
            return values[0]
        return values
