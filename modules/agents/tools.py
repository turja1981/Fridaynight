from __future__ import annotations
import math
from datetime import datetime


class ToolRegistry:
    """Registry of built-in tools as Anthropic tool definitions."""

    TOOL_DEFINITIONS: list[dict] = [
        {
            "name": "web_search",
            "description": "Search the web for information on a given query.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"],
            },
        },
        {
            "name": "document_lookup",
            "description": "Look up relevant documents from the knowledge base using RAG.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Document search query"}
                },
                "required": ["query"],
            },
        },
        {
            "name": "calculator",
            "description": "Evaluate a mathematical expression safely.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate, e.g. '2 + 2 * 10'",
                    }
                },
                "required": ["expression"],
            },
        },
        {
            "name": "datetime_tool",
            "description": "Get the current date and time.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "data_query",
            "description": "Query sample business data by key.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Data key to look up"}
                },
                "required": ["key"],
            },
        },
    ]

    _SAMPLE_DATA: dict = {
        "claim_CLM001": {"id": "CLM-2024-001", "status": "pending", "amount": 15000, "type": "auto"},
        "claim_CLM002": {"id": "CLM-2024-002", "status": "approved", "amount": 8500, "type": "health"},
        "policy_POL001": {"id": "POL-2024-001", "holder": "John Doe", "premium": 1200, "coverage": 500000},
        "account_ACC001": {"id": "ACC-001", "balance": 45230.50, "type": "savings"},
        "product_P001": {"id": "P-001", "name": "Laptop Pro", "price": 85000, "stock": 42},
    }

    def get_all_tools(self) -> list[dict]:
        """Return all Anthropic-format tool definitions."""
        return self.TOOL_DEFINITIONS

    def get_tools_by_name(self, names: list[str]) -> list[dict]:
        """Return tool definitions filtered by name list."""
        return [t for t in self.TOOL_DEFINITIONS if t["name"] in names]

    def execute(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool by name and return result as string."""
        if tool_name == "web_search":
            query = tool_input.get("query", "")
            return f"Search results for '{query}': Found 3 relevant articles about {query}. Key findings: (1) Recent industry reports indicate growth trends. (2) Expert analysis suggests improved outcomes. (3) Case studies demonstrate practical applications."

        if tool_name == "document_lookup":
            query = tool_input.get("query", "")
            try:
                from modules.rag.pipeline import RagPipeline
                pipeline = RagPipeline()
                result = pipeline.run(query)
                return result["context"]
            except Exception as e:
                return f"Document lookup for '{query}': No documents currently indexed. Please ingest documents first. Error: {str(e)}"

        if tool_name == "calculator":
            expression = tool_input.get("expression", "0")
            # Safe eval: only allow math operations
            allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
            allowed_names["abs"] = abs
            allowed_names["round"] = round
            try:
                result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
                return str(result)
            except Exception as e:
                return f"Calculation error: {e}"

        if tool_name == "datetime_tool":
            return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        if tool_name == "data_query":
            key = tool_input.get("key", "")
            data = self._SAMPLE_DATA.get(key)
            if data:
                return str(data)
            # Try partial match
            matches = {k: v for k, v in self._SAMPLE_DATA.items() if key.lower() in k.lower()}
            if matches:
                return str(matches)
            return f"No data found for key '{key}'. Available keys: {list(self._SAMPLE_DATA.keys())}"

        return f"Unknown tool: {tool_name}"
