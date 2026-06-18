from __future__ import annotations
import anthropic
from .tools import ToolRegistry


class BaseAgent:
    """ReAct agent using the raw Anthropic SDK with manual tool-use loop."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: list | None = None,
        model: str = "claude-sonnet-4-6",
        anthropic_api_key: str = "",
        max_iterations: int = 10,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools if tools is not None else []
        self.max_iterations = max_iterations
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self._registry = ToolRegistry()

    def run(self, user_message: str) -> dict:
        """Run the agent with tool-use loop and return response with metadata."""
        messages: list[dict] = [{"role": "user", "content": user_message}]
        tool_calls: list[dict] = []
        iterations = 0
        tokens_used = 0

        while iterations < self.max_iterations:
            iterations += 1
            kwargs: dict = {
                "model": self.model,
                "max_tokens": 2048,
                "system": self.system_prompt,
                "messages": messages,
            }
            if self.tools:
                kwargs["tools"] = self.tools

            response = self.client.messages.create(**kwargs)
            tokens_used += response.usage.input_tokens + response.usage.output_tokens

            if response.stop_reason == "end_turn":
                text = ""
                for block in response.content:
                    if block.type == "text":
                        text = block.text
                        break
                return {
                    "response": text,
                    "agent": self.name,
                    "tool_calls": tool_calls,
                    "iterations": iterations,
                    "tokens_used": tokens_used,
                }

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._registry.execute(block.name, block.input)
                        tool_calls.append({"tool": block.name, "input": block.input})
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                messages.append({"role": "user", "content": tool_results})
            else:
                break

        return {
            "response": "",
            "agent": self.name,
            "tool_calls": tool_calls,
            "iterations": iterations,
            "tokens_used": tokens_used,
        }
