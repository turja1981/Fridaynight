from __future__ import annotations
import os

import anthropic


class PromptOptimizer:
    """Optimizes prompts using LLM-as-judge comparison."""

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    def compare(
        self,
        prompt_a: str,
        prompt_b: str,
        test_inputs: list[str],
    ) -> dict:
        """Compare two prompts using LLM-as-judge on test inputs."""
        scores_a = 0.0
        scores_b = 0.0
        evaluations: list[dict] = []

        for test_input in test_inputs[:5]:  # limit to 5 inputs
            # Get response from prompt A
            resp_a = self._client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt_a + "\n\n" + test_input}],
            )
            response_a = resp_a.content[0].text if resp_a.content else ""

            # Get response from prompt B
            resp_b = self._client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt_b + "\n\n" + test_input}],
            )
            response_b = resp_b.content[0].text if resp_b.content else ""

            # Judge comparison
            judge_prompt = (
                f"You are an impartial AI judge. Compare these two responses to the same input.\n\n"
                f"Input: {test_input}\n\n"
                f"Response A:\n{response_a}\n\n"
                f"Response B:\n{response_b}\n\n"
                "Which response is better? Reply with ONLY 'A' or 'B' followed by a brief reason."
            )
            judge_resp = self._client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=128,
                messages=[{"role": "user", "content": judge_prompt}],
            )
            verdict = judge_resp.content[0].text.strip() if judge_resp.content else "B"

            if verdict.startswith("A"):
                scores_a += 1
            else:
                scores_b += 1

            evaluations.append(
                {
                    "input": test_input,
                    "response_a": response_a[:200],
                    "response_b": response_b[:200],
                    "verdict": verdict[:100],
                }
            )

        total = len(test_inputs[:5])
        winner = "A" if scores_a > scores_b else "B"
        return {
            "winner": winner,
            "score_a": scores_a / total if total > 0 else 0,
            "score_b": scores_b / total if total > 0 else 0,
            "evaluations": evaluations,
        }
