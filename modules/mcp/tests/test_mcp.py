from __future__ import annotations
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI


@pytest.fixture
def client():
    from modules.mcp.server import mcp_router
    app = FastAPI()
    app.include_router(mcp_router)
    return TestClient(app)


class TestMCPServer:
    def test_tools_list_returns_jsonrpc(self, client):
        response = client.post("/mcp/tools/list")
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "tools" in data["result"]

    def test_tools_list_has_expected_tools(self, client):
        response = client.post("/mcp/tools/list")
        tools = {t["name"] for t in response.json()["result"]["tools"]}
        assert "calculator" in tools
        assert "datetime_tool" in tools

    def test_calculator_tool_call(self, client):
        response = client.post(
            "/mcp/tools/call",
            json={"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "calculator", "arguments": {"expression": "2 + 2"}}, "id": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        content = data["result"]["content"]
        assert isinstance(content, list)
        assert any("4" in str(c.get("text", "")) for c in content)

    def test_datetime_tool_call(self, client):
        response = client.post(
            "/mcp/tools/call",
            json={"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "datetime_tool", "arguments": {}}, "id": 2},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        text = data["result"]["content"][0]["text"]
        assert "UTC" in text or len(text) > 5

    def test_unknown_tool_returns_error(self, client):
        response = client.post(
            "/mcp/tools/call",
            json={"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "nonexistent_tool", "arguments": {}}, "id": 3},
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32601

    def test_response_includes_id(self, client):
        response = client.post(
            "/mcp/tools/call",
            json={"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "datetime_tool", "arguments": {}}, "id": 42},
        )
        assert response.json()["id"] == 42
