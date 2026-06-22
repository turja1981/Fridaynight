from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock

try:
    import deepeval  # noqa: F401
    HAS_DEEPEVAL = True
except ImportError:
    HAS_DEEPEVAL = False

pytestmark = pytest.mark.skipif(not HAS_DEEPEVAL, reason="deepeval not available")


def test_rag_evaluator_single():
    """RAGEvaluator returns expected score keys."""
    from modules.evaluation.rag_evaluator import RAGEvaluator
    evaluator = RAGEvaluator()
    mock_result = {"faithfulness": 0.9, "answer_relevancy": 0.85, "context_precision": 0.8, "context_recall": 0.75}
    with patch("modules.evaluation.rag_evaluator.evaluate", return_value=MagicMock(to_pandas=lambda: MagicMock(mean=lambda: MagicMock(to_dict=lambda: mock_result)))):
        result = evaluator.evaluate_single("What is claim CLM-001?", "Claim CLM-001 is under review.", ["Claim CLM-001 is under review with amount 15000."])
    assert "faithfulness" in result or result == mock_result

def test_llm_evaluator_structure():
    """LLMEvaluator returns correct keys."""
    from modules.evaluation.llm_evaluator import LLMEvaluator
    evaluator = LLMEvaluator()
    mock_metric = MagicMock()
    mock_metric.score = 0.85
    mock_metric.is_successful.return_value = True
    mock_metric.reason = "Test reason"
    with patch("modules.evaluation.llm_evaluator.HallucinationMetric", return_value=mock_metric), \
         patch("modules.evaluation.llm_evaluator.AnswerRelevancyMetric", return_value=mock_metric), \
         patch("modules.evaluation.llm_evaluator.ToxicityMetric", return_value=mock_metric):
        result = evaluator.run_full_eval("What is this?", "This is a test.", ["Test context."])
    assert "overall_pass" in result
    assert "hallucination" in result
