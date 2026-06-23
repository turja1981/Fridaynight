from __future__ import annotations

try:
    from deepeval import evaluate as deepeval_evaluate
    from deepeval.test_case import LLMTestCase
    from deepeval.metrics import (
        HallucinationMetric,
        AnswerRelevancyMetric,
        FaithfulnessMetric,
        BiasMetric,
        ToxicityMetric,
    )
    _DEEPEVAL_AVAILABLE = True
except ImportError:
    _DEEPEVAL_AVAILABLE = False
    HallucinationMetric = None
    AnswerRelevancyMetric = None
    FaithfulnessMetric = None
    BiasMetric = None
    ToxicityMetric = None


class LLMEvaluator:
    """DeepEval-based LLM output quality evaluator."""

    def __init__(self, model: str = "claude-sonnet-4-6", threshold: float = 0.7):
        self.threshold = threshold
        self.model = model

    def _make_test_case(
        self,
        input_text: str,
        actual_output: str,
        expected_output: str | None = None,
        retrieval_context: list[str] | None = None,
    ):
        if not _DEEPEVAL_AVAILABLE:
            raise ImportError("deepeval is not available in this environment")
        return LLMTestCase(
            input=input_text,
            actual_output=actual_output,
            expected_output=expected_output,
            retrieval_context=retrieval_context or [],
        )

    def check_hallucination(self, input_text: str, output: str, context: list[str]) -> dict:
        metric = HallucinationMetric(threshold=self.threshold)
        tc = self._make_test_case(input_text, output, retrieval_context=context)
        metric.measure(tc)
        return {"score": metric.score, "passed": metric.is_successful(), "reason": metric.reason}

    def check_answer_relevancy(self, input_text: str, output: str) -> dict:
        metric = AnswerRelevancyMetric(threshold=self.threshold)
        tc = self._make_test_case(input_text, output)
        metric.measure(tc)
        return {"score": metric.score, "passed": metric.is_successful(), "reason": metric.reason}

    def check_toxicity(self, input_text: str, output: str) -> dict:
        metric = ToxicityMetric(threshold=self.threshold)
        tc = self._make_test_case(input_text, output)
        metric.measure(tc)
        return {"score": metric.score, "passed": metric.is_successful(), "reason": metric.reason}

    def run_full_eval(
        self,
        input_text: str,
        output: str,
        context: list[str] | None = None,
    ) -> dict:
        """Run hallucination + relevancy + toxicity checks."""
        results = {}
        results["hallucination"] = self.check_hallucination(input_text, output, context or [])
        results["answer_relevancy"] = self.check_answer_relevancy(input_text, output)
        results["toxicity"] = self.check_toxicity(input_text, output)
        results["overall_pass"] = all(v["passed"] for v in results.values())
        return results
