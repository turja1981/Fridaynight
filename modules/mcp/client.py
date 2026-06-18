from __future__ import annotations
from typing import Any

import httpx


class MCPClient:
    """HTTP client for interacting with an MCP server."""

    def __init__(self, server_url: str) -> None:
        self.server_url = server_url.rstrip("/")

    def list_tools(self) -> list[dict]:
        """List tools available on the MCP server."""
        with httpx.Client() as client:
            response = client.post(
                f"{self.server_url}/mcp/tools/list",
                json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("result", {}).get("tools", [])

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call a specific tool on the MCP server."""
        with httpx.Client() as client:
            response = client.post(
                f"{self.server_url}/mcp/tools/call",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "id": 1,
                    "params": {"name": tool_name, "arguments": arguments},
                },
            )
            response.raise_for_status()
            return response.json()
