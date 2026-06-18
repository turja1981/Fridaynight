from __future__ import annotations


class PromptTemplate:
    """A reusable prompt template with optional few-shot examples and CoT."""

    def __init__(
        self,
        template: str,
        few_shot_examples: list[dict] | None = None,
        chain_of_thought: bool = False,
    ) -> None:
        self.template = template
        self.few_shot_examples = few_shot_examples or []
        self.chain_of_thought = chain_of_thought

    def render(self, **kwargs) -> str:
        """Render the template with provided variables."""
        prompt = self.template.format(**kwargs)

        if self.few_shot_examples:
            examples_text = "\n\nExamples:\n"
            for ex in self.few_shot_examples:
                role = ex.get("role", "user")
                content = ex.get("content", "")
                examples_text += f"{role.capitalize()}: {content}\n"
            prompt = examples_text.strip() + "\n\n" + prompt

        if self.chain_of_thought:
            prompt += "\n\nLet's think step by step:"

        return prompt


TEMPLATES: dict[str, PromptTemplate] = {
    "SUMMARIZE": PromptTemplate(
        template=(
            "Please summarize the following text concisely, capturing the key points:\n\n"
            "Text: {text}\n\n"
            "Summary:"
        ),
    ),
    "CLASSIFY": PromptTemplate(
        template=(
            "Classify the following text into one of these categories: {categories}\n\n"
            "Text: {text}\n\n"
            "Category:"
        ),
        chain_of_thought=True,
    ),
    "EXTRACT_ENTITIES": PromptTemplate(
        template=(
            "Extract all named entities from the following text. "
            "Return as JSON with keys: persons, organizations, locations, dates, amounts.\n\n"
            "Text: {text}\n\n"
            "Entities:"
        ),
    ),
    "GENERATE_REPORT": PromptTemplate(
        template=(
            "Generate a professional {report_type} report based on the following data:\n\n"
            "{data}\n\n"
            "The report should include: executive summary, key findings, recommendations, and conclusion.\n\n"
            "Report:"
        ),
    ),
    "ANALYZE_DOCUMENT": PromptTemplate(
        template=(
            "Analyze the following document and provide:\n"
            "1. Document type and purpose\n"
            "2. Key information extracted\n"
            "3. Action items or next steps\n"
            "4. Risk assessment (if applicable)\n\n"
            "Document:\n{document}\n\n"
            "Analysis:"
        ),
        chain_of_thought=True,
    ),
    "CUSTOMER_SERVICE_RESPOND": PromptTemplate(
        template=(
            "You are a helpful customer service agent for {company}. "
            "Respond to the following customer query professionally and empathetically.\n\n"
            "Customer Query: {query}\n\n"
            "Relevant Context: {context}\n\n"
            "Response:"
        ),
        few_shot_examples=[
            {
                "role": "user",
                "content": "Customer Query: When will my claim be processed?\nResponse: Thank you for reaching out. Your claim is currently under review and will be processed within 3-5 business days.",
            }
        ],
    ),
    "FRAUD_ANALYSIS": PromptTemplate(
        template=(
            "Analyze the following transaction/claim for potential fraud indicators.\n\n"
            "Data: {data}\n\n"
            "Provide: risk_score (0-100), fraud_indicators (list), recommended_action, confidence_level.\n\n"
            "Analysis:"
        ),
        chain_of_thought=True,
    ),
}
