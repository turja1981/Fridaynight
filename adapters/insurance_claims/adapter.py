from __future__ import annotations
import json

from adapters.base import BaseAdapter

_SAMPLE_CLAIMS = [
    {
        "claim_id": "CLM-2024-001",
        "policy_number": "POL-INS-98765",
        "claimant": "Rajesh Kumar",
        "type": "Motor Vehicle Accident",
        "date_of_incident": "2024-03-15",
        "date_filed": "2024-03-16",
        "status": "Under Review",
        "claimed_amount": 85000,
        "approved_amount": None,
        "description": "Rear-end collision at Bangalore Highway. Significant damage to rear bumper and trunk.",
        "fraud_indicators": ["filed within 24h of renewal"],
        "adjuster": "Priya Sharma",
    },
    {
        "claim_id": "CLM-2024-002",
        "policy_number": "POL-HEALTH-44321",
        "claimant": "Ananya Patel",
        "type": "Health — Hospitalization",
        "date_of_incident": "2024-03-10",
        "date_filed": "2024-03-12",
        "status": "Approved",
        "claimed_amount": 45000,
        "approved_amount": 42000,
        "description": "Emergency appendectomy at Apollo Hospital, Mumbai. All documents verified.",
        "fraud_indicators": [],
        "adjuster": "Mohammed Ali",
    },
    {
        "claim_id": "CLM-2024-003",
        "policy_number": "POL-HOME-77890",
        "claimant": "Suresh Menon",
        "type": "Property — Water Damage",
        "date_of_incident": "2024-02-28",
        "date_filed": "2024-03-01",
        "status": "Pending Investigation",
        "claimed_amount": 320000,
        "approved_amount": None,
        "description": "Flood damage to ground floor. Claiming furniture, electronics, and structural damage.",
        "fraud_indicators": ["claimed amount 3x higher than assessed value", "previous claim within 2 years"],
        "adjuster": "Deepika Singh",
    },
]


class InsuranceClaimsAdapter(BaseAdapter):
    """Adapter for Insurance Claims Processing domain."""

    domain_name = "Insurance Claims Processing"

    system_prompt = (
        "You are an expert Insurance Claims Processing AI Agent for EnterpriseCorp Insurance. "
        "Your core responsibilities:\n"
        "1. CLAIM ANALYSIS: Thoroughly analyze submitted claims for completeness, validity, and potential fraud\n"
        "2. POLICY VALIDATION: Cross-reference claims against policy terms, coverage limits, and exclusions\n"
        "3. FRAUD DETECTION: Identify red flags such as timing anomalies, inflated amounts, repeat claims\n"
        "4. SETTLEMENT CALCULATION: Compute fair settlement amounts considering deductibles, depreciation, and coverage\n"
        "5. ADJUSTER ROUTING: Route complex or high-value claims (>₹500,000) to senior adjusters\n"
        "6. CUSTOMER COMMUNICATION: Provide clear, empathetic status updates to claimants\n\n"
        "Guidelines:\n"
        "- Always ask for claim ID before looking up details\n"
        "- Flag fraud risk as: LOW (0-30%), MEDIUM (31-60%), HIGH (61-100%)\n"
        "- Follow IRDAI regulatory guidelines\n"
        "- Never approve claims exceeding policy limits\n"
        "- Escalate when: fraud risk > 60%, claim > ₹1,000,000, or legal dispute mentioned"
    )

    kpi_definitions = {
        "claim_processing_time": "Average time from claim submission to final decision (target: <3 business days)",
        "auto_approval_rate": "Percentage of claims approved automatically without human review (target: >40%)",
        "fraud_detection_rate": "Percentage of fraudulent claims correctly identified (target: >90%)",
        "customer_satisfaction": "Post-claim CSAT score 1-5 (target: >4.0)",
        "cost_per_claim": "Operational cost per claim processed in USD (target: <$15)",
    }

    suggested_tools = ["document_lookup", "data_query", "calculator", "datetime_tool"]

    sample_questions = [
        "What is the status of claim CLM-2024-001?",
        "Analyze this damage photo for settlement estimation",
        "Calculate the settlement for a motor claim with ₹85,000 damage and ₹5,000 deductible",
        "Is there any fraud risk in claim CLM-2024-003?",
        "List all pending claims filed this week",
        "What documents are required for a health insurance claim?",
        "How long does claim processing typically take?",
    ]

    def get_config(self) -> dict:
        """Return insurance claims adapter configuration."""
        return {
            "domain_name": self.domain_name,
            "system_prompt": self.system_prompt,
            "kpi_definitions": self.kpi_definitions,
            "suggested_tools": self.suggested_tools,
            "sample_questions": self.sample_questions,
        }

    def get_sample_context(self) -> str:
        """Return sample claims data as context."""
        return (
            f"Insurance Claims Database — {len(_SAMPLE_CLAIMS)} active claims:\n\n"
            + json.dumps(_SAMPLE_CLAIMS, indent=2)
        )
