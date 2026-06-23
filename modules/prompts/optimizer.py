from __future__ import annotations
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

class PromptOptimizer:
    """A/B tests prompts using LLM-as-judge to find the best variant."""

    def __init__(self, model: str = "claude-haiku-4-5-20251001", anthropic_api_key: str = ""):
        self.llm = ChatAnthropic(model=model, api_key=anthropic_api_key, max_tokens=256)

    def compare(self, prompt_a: str, prompt_b: str, test_input: str) -> dict:
        """Compare two prompt variants on a test input using LLM judge."""
        response_a = self.llm.invoke([HumanMessage(content=prompt_a.replace("{input}", test_input))]).content
        response_b = self.llm.invoke([HumanMessage(content=prompt_b.replace("{input}", test_input))]).content

        judge_prompt = f"""Compare these two AI responses and pick the better one.

Response A: {response_a}

Response B: {response_b}

Criteria: accuracy, clarity, helpfulness, conciseness.
Reply with only: "A" or "B" and one sentence reason."""

        judgment = self.llm.invoke([HumanMessage(content=judge_prompt)]).content.strip()
        winner = "A" if judgment.startswith("A") else "B"
        return {"winner": winner, "judgment": judgment, "response_a": response_a, "response_b": response_b}
