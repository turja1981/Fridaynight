from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest


def _make_mock_text_response(text: str = "Test response", input_tokens: int = 100, output_tokens: int = 50):
    """Create a mock Anthropic text response."""
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = text

    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [mock_block]
    mock_response.usage.input_tokens = input_tokens
    mock_response.usage.output_tokens = output_tokens
    return mock_response


def _make_mock_tool_use_response(tool_name: str, tool_input: dict, tool_id: str = "tool_123"):
    """Create a mock Anthropic tool_use response."""
    mock_tool_block = MagicMock()
    mock_tool_block.type = "tool_use"
    mock_tool_block.name = tool_name
    mock_tool_block.input = tool_input
    mock_tool_block.id = tool_id

    mock_response = MagicMock()
    mock_response.stop_reason = "tool_use"
    mock_response.content = [mock_tool_block]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    return mock_response


class TestToolRegistry:
    def test_get_all_tools_returns_list(self):
        from modules.agents.tools import ToolRegistry
        registry = ToolRegistry()
        tools = registry.get_all_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_tool_definitions_have_required_fields(self):
        from modules.agents.tools import ToolRegistry
        registry = ToolRegistry()
        for tool in registry.get_all_tools():
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool

    def test_calculator_tool(self):
        from modules.agents.tools import ToolRegistry
        registry = ToolRegistry()
        result = registry.execute("calculator", {"expression": "2 + 2"})
        assert result == "4"

    def test_calculator_complex_expression(self):
        from modules.agents.tools import ToolRegistry
        registry = ToolRegistry()
        result = registry.execute("calculator", {"expression": "10 * 5 + 3"})
        assert result == "53"

    def test_datetime_tool(self):
        from modules.agents.tools import ToolRegistry
        registry = ToolRegistry()
        result = registry.execute("datetime_tool", {})
        assert "UTC" in result

    def test_data_query_tool_existing_key(self):
        from modules.agents.tools import ToolRegistry
        registry = ToolRegistry()
        result = registry.execute("data_query", {"key": "claim_CLM001"})
        assert "CLM-2024-001" in result

    def test_data_query_tool_missing_key(self):
        from modules.agents.tools import ToolRegistry
        registry = ToolRegistry()
        result = registry.execute("data_query", {"key": "nonexistent_key"})
        assert "No data found" in result

    def test_web_search_tool(self):
        from modules.agents.tools import ToolRegistry
        registry = ToolRegistry()
        result = registry.execute("web_search", {"query": "AI insurance claims"})
        assert "AI insurance claims" in result

    def test_get_tools_by_name(self):
        from modules.agents.tools import ToolRegistry
        registry = ToolRegistry()
        tools = registry.get_tools_by_name(["calculator", "datetime_tool"])
        assert len(tools) == 2
        names = [t["name"] for t in tools]
        assert "calculator" in names
        assert "datetime_tool" in names


class TestBaseAgent:
    @patch("modules.agents.base_agent.anthropic.Anthropic")
    def test_run_end_turn(self, mock_anthropic_class):
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.return_value = _make_mock_text_response("Hello, I can help you.")

        from modules.agents.base_agent import BaseAgent
        agent = BaseAgent("test_agent", "You are helpful.", [])
        result = agent.run("Hello")

        assert "response" in result
        assert result["response"] == "Hello, I can help you."
        assert "tool_calls" in result
        assert result["iterations"] == 1
        assert result["tokens_used"] == 150

    @patch("modules.agents.base_agent.anthropic.Anthropic")
    def test_run_with_tool_use(self, mock_anthropic_class):
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # First call: tool_use, second call: end_turn
        mock_client.messages.create.side_effect = [
            _make_mock_tool_use_response("calculator", {"expression": "2 + 2"}),
            _make_mock_text_response("The answer is 4."),
        ]

        from modules.agents.base_agent import BaseAgent
        from modules.agents.tools import ToolRegistry
        tools = ToolRegistry().get_tools_by_name(["calculator"])
        agent = BaseAgent("test_agent", "You are helpful.", tools)
        result = agent.run("What is 2 + 2?")

        assert result["iterations"] == 2
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["tool"] == "calculator"


class TestAgentOrchestrator:
    def test_route_customer_service(self):
        from modules.agents.orchestrator import AgentOrchestrator
        orch = AgentOrchestrator()
        agent_name = orch.route("What is the status of my claim?")
        assert agent_name == "customer_service_agent"

    def test_route_analysis(self):
        from modules.agents.orchestrator import AgentOrchestrator
        orch = AgentOrchestrator()
        agent_name = orch.route("analyze the performance metrics")
        assert agent_name == "analysis_agent"

    def test_route_data(self):
        from modules.agents.orchestrator import AgentOrchestrator
        orch = AgentOrchestrator()
        agent_name = orch.route("query the data for account details")
        assert agent_name in ["data_agent", "customer_service_agent"]  # both match

    def test_route_unknown_defaults_to_research(self):
        from modules.agents.orchestrator import AgentOrchestrator
        orch = AgentOrchestrator()
        agent_name = orch.route("xyzzy completely unknown task")
        assert agent_name == "research_agent"

    def test_list_agents(self):
        from modules.agents.orchestrator import AgentOrchestrator
        orch = AgentOrchestrator()
        agents = orch.list_agents()
        assert len(agents) == 4
        names = [a["name"] for a in agents]
        assert "research_agent" in names
        assert "analysis_agent" in names
        assert "customer_service_agent" in names
        assert "data_agent" in names

    @patch("modules.agents.base_agent.anthropic.Anthropic")
    def test_run_auto_routing(self, mock_anthropic_class):
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.return_value = _make_mock_text_response("Claim status: pending.")

        from modules.agents.orchestrator import AgentOrchestrator
        orch = AgentOrchestrator()
        result = orch.run("What is my claim status?")
        assert "agent_used" in result
        assert "response" in result
