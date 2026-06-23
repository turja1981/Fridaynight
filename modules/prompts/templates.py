from __future__ import annotations
from dataclasses import dataclass, field
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

@dataclass
class PromptTemplate:
    """Structured prompt with optional few-shot examples and CoT prefix."""
    name: str
    template: str
    variables: list[str] = field(default_factory=list)
    few_shot_examples: list[dict] = field(default_factory=list)
    chain_of_thought: bool = False

    def render(self, **kwargs) -> str:
        result = self.template
        if self.chain_of_thought:
            result += "\n\nLet me think through this step by step:"
        for k, v in kwargs.items():
            result = result.replace(f"{{{k}}}", str(v))
        return result

    def as_langchain_template(self) -> ChatPromptTemplate:
        messages = []
        if self.few_shot_examples:
            example_prompt = ChatPromptTemplate.from_messages([("human", "{input}"), ("ai", "{output}")])
            few_shot = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=self.few_shot_examples)
            messages.append(few_shot)
        messages.append(("human", self.template))
        return ChatPromptTemplate.from_messages(messages)

PROMPT_TEMPLATES: dict[str, PromptTemplate] = {
    "SUMMARIZE": PromptTemplate(
        name="SUMMARIZE",
        template="Summarize the following text in {max_words} words or less:\n\n{text}",
        variables=["text", "max_words"],
        chain_of_thought=False,
    ),
    "CLASSIFY": PromptTemplate(
        name="CLASSIFY",
        template="Classify the following into one of these categories: {categories}\n\nText: {text}\n\nRespond with only the category name.",
        variables=["text", "categories"],
        few_shot_examples=[
            {"input": "My car was stolen last night", "output": "Auto Theft"},
            {"input": "Water damage from burst pipe", "output": "Property Damage"},
        ],
    ),
    "EXTRACT_ENTITIES": PromptTemplate(
        name="EXTRACT_ENTITIES",
        template="Extract the following entities from this text: {entity_types}\n\nText: {text}\n\nReturn as JSON.",
        variables=["text", "entity_types"],
        chain_of_thought=True,
    ),
    "GENERATE_REPORT": PromptTemplate(
        name="GENERATE_REPORT",
        template="Generate a professional {report_type} report based on:\n\n{data}\n\nFormat with sections: Executive Summary, Key Findings, Recommendations.",
        variables=["report_type", "data"],
        chain_of_thought=True,
    ),
    "CUSTOMER_SERVICE_RESPOND": PromptTemplate(
        name="CUSTOMER_SERVICE_RESPOND",
        template="As a {company} customer service representative, respond to:\n\nCustomer: {message}\n\nContext: {context}\n\nBe empathetic, concise, and solution-focused.",
        variables=["company", "message", "context"],
        few_shot_examples=[
            {"input": "My claim is taking too long", "output": "I understand your frustration. Claim CLM-001 is currently in the review stage. I'm escalating this to a senior adjuster for priority processing."},
        ],
    ),
    "FRAUD_ANALYSIS": PromptTemplate(
        name="FRAUD_ANALYSIS",
        template="Analyze this transaction/claim for fraud indicators:\n\n{data}\n\nIdentify: risk_score (0-1), red_flags (list), recommendation (APPROVE/REVIEW/REJECT).",
        variables=["data"],
        chain_of_thought=True,
    ),
}
