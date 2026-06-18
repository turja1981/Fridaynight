from __future__ import annotations
from typing import Any

from fastapi import APIRouter

from modules.agents.tools import ToolRegistry

router = APIRouter(prefix="/mcp", tags=["mcp"])


class MCPServer:
    """MCP server implemented as a FastAPI APIRouter."""

    def __init__(self) -> None:
        self._registry = ToolRegistry()
        self.router = router
        self._register_routes()

    def _register_routes(self) -> None:
        registry = self._registry

        @router.post("/tools/list")
        async def list_tools(request: dict = None) -> dict:
            """List available tools in MCP format."""
            tools = registry.get_all_tools()
            mcp_tools = [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "inputSchema": t["input_schema"],
                }
                for t in tools
            ]
            return {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"tools": mcp_tools},
            }

        @router.post("/tools/call")
        async def call_tool(body: dict) -> dict:
            """Execute a tool by name with given arguments."""
            # Support both direct and jsonrpc format
            method = body.get("method", "tools/call")
            params = body.get("params", body)
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            if not tool_name:
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id", 1),
                    "error": {"code": -32602, "message": "Missing tool name"},
                }

            try:
                result = registry.execute(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id", 1),
                    "result": {
                        "content": [{"type": "text", "text": result}],
                        "isError": False,
                    },
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id", 1),
                    "error": {"code": -32000, "message": str(e)},
                }
