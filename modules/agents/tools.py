from __future__ import annotations
import math
from datetime import datetime
from langchain.tools import tool
from langchain_core.tools import BaseTool


@tool
def calculator_tool(expression: str) -> str:
    """Evaluate a mathematical expression safely. Input: math expression string."""
    try:
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, allowed)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@tool
def datetime_tool(query: str = "") -> str:
    """Return the current date and time in UTC."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


@tool
def data_query_tool(entity_id: str) -> str:
    """Look up a business entity by ID. Input: entity ID like CLM-001 or ACC-001."""
    SAMPLE_DATA = {
        "CLM-001": {"status": "Under Review", "amount": 15000, "type": "Auto Accident", "days_open": 3},
        "CLM-002": {"status": "Approved", "amount": 5200, "type": "Property Damage", "days_open": 7},
        "ACC-001": {"holder": "Rajesh Kumar", "policy": "COMP-2024", "premium": 12000},
        "TXN-001": {"amount": 45000, "type": "Wire Transfer", "risk_score": 0.8, "flag": "High Risk"},
    }
    result = SAMPLE_DATA.get(entity_id.upper())
    return str(result) if result else f"No record found for {entity_id}"


@tool
def web_search_tool(query: str) -> str:
    """Search for information on a topic. Input: search query string."""
    return f"[Mock search results for: '{query}'] Found 3 relevant articles about enterprise AI applications in {query.split()[0]} domain."


def get_all_tools() -> list[BaseTool]:
    """Return all registered LangChain tools (used by HITLOrchestrator)."""
    return [calculator_tool, datetime_tool, data_query_tool, web_search_tool]


class ToolRegistry:
    """Dict-based tool registry for use with raw Anthropic SDK agents."""

    _SAMPLE_DATA: dict = {
        "claim_CLM001": {
            "id": "CLM-2024-001",
            "status": "Under Review",
            "amount": 15000,
            "type": "Auto Accident",
            "claimant": "Rahul Sharma",
            "days_open": 3,
        },
        "acc_001": {
            "id": "ACC-001",
            "holder": "Priya Patel",
            "policy": "COMP-2024",
            "premium": 12000,
        },
        "txn_001": {
            "id": "TXN-001",
            "amount": 45000,
            "type": "Wire Transfer",
            "risk_score": 0.8,
            "flag": "High Risk",
        },
    }

    _TOOL_DEFS: list[dict] = [
        {
            "name": "calculator",
            "description": "Evaluate a mathematical expression safely.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression to evaluate"},
                },
                "required": ["expression"],
            },
        },
        {
            "name": "datetime_tool",
            "description": "Return the current date and time in UTC.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "data_query",
            "description": "Look up a business entity by key.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Entity key to look up"},
                },
                "required": ["key"],
            },
        },
        {
            "name": "web_search",
            "description": "Search for information on a topic.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string"},
                },
                "required": ["query"],
            },
        },
    ]

    def get_all_tools(self) -> list[dict]:
        return list(self._TOOL_DEFS)

    def get_tools_by_name(self, names: list[str]) -> list[dict]:
        return [t for t in self._TOOL_DEFS if t["name"] in names]

    def execute(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "calculator":
            try:
                allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
                result = eval(tool_input.get("expression", ""), {"__builtins__": {}}, allowed)  # noqa: S307
                return str(result)
            except Exception as e:
                return f"Error: {e}"
        if tool_name == "datetime_tool":
            return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        if tool_name == "data_query":
            key = tool_input.get("key", "")
            result = self._SAMPLE_DATA.get(key)
            return str(result) if result else f"No data found for key: {key}"
        if tool_name == "web_search":
            query = tool_input.get("query", "")
            return f"[Search results for: '{query}'] Found 3 relevant articles about {query}."
        return f"Unknown tool: {tool_name}"
