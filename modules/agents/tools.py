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
    """Return the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
    """Return all registered LangChain tools."""
    return [calculator_tool, datetime_tool, data_query_tool, web_search_tool]
