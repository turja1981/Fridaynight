from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from modules.agents.tools import get_all_tools

mcp_router = APIRouter(prefix="/mcp", tags=["mcp"])

TOOL_DESCRIPTIONS = {
    t.name: {"name": t.name, "description": t.description, "input_schema": {"type": "object", "properties": {}}}
    for t in get_all_tools()
}

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict = {}
    id: int = 1

@mcp_router.post("/tools/list")
async def list_tools():
    return {"jsonrpc": "2.0", "result": {"tools": list(TOOL_DESCRIPTIONS.values())}, "id": 1}

@mcp_router.post("/tools/call")
async def call_tool(req: MCPRequest):
    tool_name = req.params.get("name")
    args = req.params.get("arguments", {})
    tools = {t.name: t for t in get_all_tools()}
    if tool_name not in tools:
        return {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Tool {tool_name} not found"}, "id": req.id}
    result = tools[tool_name].invoke(args)
    return {"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": str(result)}]}, "id": req.id}
