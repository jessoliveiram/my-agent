from src.graph.tools import McpCalendarReadTool, McpCalendarWriteTool


class FakeMcpClient:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return self.result


def test_mcp_calendar_read_tool_maps_arguments():
    client = FakeMcpClient([{"summary": "Planning"}])
    tool = McpCalendarReadTool(client)

    result = tool.list_events(max_results=5, calendar_id="work")

    assert result == [{"summary": "Planning"}]
    assert client.calls == [
        ("upcoming_events", {"max_results": 5, "calendar_id": "work"})
    ]


def test_mcp_calendar_write_tool_maps_arguments():
    event = {"summary": "Planning"}
    client = FakeMcpClient({"id": "event-1"})
    tool = McpCalendarWriteTool(client)

    result = tool.create_event(event, calendar_id="work")

    assert result == {"id": "event-1"}
    name, arguments = client.calls[0]
    assert name == "add_event"
    assert arguments["event_body"] == event
    assert arguments["calendar_id"] == "work"
    assert arguments["confirmed"] is True
    assert len(arguments["idempotency_key"]) == 64


def test_mcp_calendar_tools_reject_invalid_result_shapes():
    read_tool = McpCalendarReadTool(FakeMcpClient({"items": []}))
    write_tool = McpCalendarWriteTool(FakeMcpClient([]))

    try:
        read_tool.list_events()
        raise AssertionError("read adapter accepted an invalid result")
    except RuntimeError as exc:
        assert "invalid result" in str(exc)

    try:
        write_tool.create_event({"summary": "Planning"})
        raise AssertionError("write adapter accepted an invalid result")
    except RuntimeError as exc:
        assert "invalid result" in str(exc)
