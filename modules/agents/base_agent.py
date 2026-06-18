from __future__ import annotations
import os
from typing import Any

import anthropic


class BaseAgent:
    """Base agent that implements the Anthropic tool-use loop."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: list[dict],
        model: str = "claude-sonnet-4-6",
    ) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.model = model
        self._client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool by name and return string result."""
        from .tools import ToolRegistry
        registry = ToolRegistry()
        return registry.execute(tool_name, tool_input)

    def run(self, user_message: str) -> dict:
        """Run agent with tool-use loop, max 10 iterations."""
        messages: list[dict] = [{"role": "user", "content": user_message}]
        all_tool_calls: list[dict] = []
        iterations = 0
        total_tokens = 0

        while iterations < 10:
            iterations += 1
            response = self._client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                tools=self.tools if self.tools else [],
                messages=messages,
            )
            total_tokens += response.usage.input_tokens + response.usage.output_tokens

            if response.stop_reason == "end_turn":
                # Extract text from content blocks
                text_parts = [
                    block.text
                    for block in response.content
                    if hasattr(block, "text")
                ]
                return {
                    "response": "\n".join(text_parts),
                    "tool_calls": all_tool_calls,
                    "iterations": iterations,
                    "tokens_used": total_tokens,
                }

            if response.stop_reason == "tool_use":
                # Add assistant response to messages
                messages.append({"role": "assistant", "content": response.content})

                # Execute each tool call
                tool_results: list[dict] = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_result = self._execute_tool(tool_name, tool_input)
                        all_tool_calls.append(
                            {
                                "tool": tool_name,
                                "input": tool_input,
                                "result": tool_result,
                            }
                        )
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": tool_result,
                            }
                        )

                messages.append({"role": "user", "content": tool_results})
            else:
                # Unknown stop reason, extract what we have
                text_parts = [
                    block.text
                    for block in response.content
                    if hasattr(block, "text")
                ]
                return {
                    "response": "\n".join(text_parts),
                    "tool_calls": all_tool_calls,
                    "iterations": iterations,
                    "tokens_used": total_tokens,
                }

        # Max iterations reached
        return {
            "response": "Maximum iterations reached.",
            "tool_calls": all_tool_calls,
            "iterations": iterations,
            "tokens_used": total_tokens,
        }
