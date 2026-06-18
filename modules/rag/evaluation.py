from __future__ import annotations

try:
    from datasets import Dataset
    from ragas import evaluate as _ragas_evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        answer_correctness,
    )
    _RAGAS_AVAILABLE = True
except ImportError:
    _RAGAS_AVAILABLE = False


class RAGEvaluator:
    """Evaluates RAG pipeline quality using RAGAS metrics."""

    def __init__(self, llm=None, embeddings=None):
        self.llm = llm
        self.embeddings = embeddings

    def evaluate(
        self,
        questions: list[str],
        answers: list[str],
        contexts: list[list[str]],
        ground_truths: list[str] | None = None,
    ) -> dict:
        """Run RAGAS evaluation. Returns dict of metric scores."""
        if not _RAGAS_AVAILABLE:
            raise ImportError("ragas is not available — install with: pip install ragas")
        data: dict = {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
        }
        if ground_truths:
            data["ground_truth"] = ground_truths

        dataset = Dataset.from_dict(data)
        metrics = [faithfulness, answer_relevancy, context_precision]
        if ground_truths:
            metrics += [context_recall, answer_correctness]

        result = _ragas_evaluate(dataset=dataset, metrics=metrics)
        return result.to_pandas().mean().to_dict()

    def evaluate_single(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        ground_truth: str | None = None,
    ) -> dict:
        return self.evaluate(
            [question], [answer], [contexts],
            [ground_truth] if ground_truth else None,
        )
