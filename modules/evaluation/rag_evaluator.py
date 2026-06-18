from __future__ import annotations
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

class RAGEvaluator:
    """RAGAS-based evaluation for RAG pipeline quality."""

    METRICS = [faithfulness, answer_relevancy, context_precision, context_recall]

    def evaluate_dataset(
        self,
        questions: list[str],
        answers: list[str],
        contexts: list[list[str]],
        ground_truths: list[str] | None = None,
    ) -> dict:
        """Run RAGAS over a batch. Returns avg scores per metric."""
        data: dict = {"question": questions, "answer": answers, "contexts": contexts}
        if ground_truths:
            data["ground_truth"] = ground_truths
        dataset = Dataset.from_dict(data)
        result = evaluate(dataset=dataset, metrics=self.METRICS)
        return result.to_pandas().mean().to_dict()

    def evaluate_single(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        ground_truth: str | None = None,
    ) -> dict:
        return self.evaluate_dataset(
            [question], [answer], [contexts],
            [ground_truth] if ground_truth else None,
        )

    def get_dashboard_scores(self, results: list[dict]) -> dict:
        """Format RAGAS scores for KPI dashboard display."""
        if not results:
            return {"faithfulness": 0.0, "answer_relevancy": 0.0, "context_precision": 0.0}
        qs = [r["question"] for r in results]
        ans = [r["answer"] for r in results]
        ctxs = [r.get("contexts", [r.get("context", "")]) for r in results]
        ctxs = [[c] if isinstance(c, str) else c for c in ctxs]
        return self.evaluate_dataset(qs, ans, ctxs)
