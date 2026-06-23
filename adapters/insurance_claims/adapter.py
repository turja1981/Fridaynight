from __future__ import annotations
from adapters.base import BaseAdapter
import json

SAMPLE_CLAIMS = [
    {"claim_id": "CLM-001", "policy": "COMP-2024-8823", "type": "Auto Accident", "amount": 15000, "status": "Under Review", "date": "2024-06-10", "description": "Rear-end collision on NH-48. Vehicle damage to bumper and trunk."},
    {"claim_id": "CLM-002", "policy": "HOME-2023-4411", "type": "Water Damage", "amount": 85000, "status": "Approved", "date": "2024-06-08", "description": "Burst pipe in kitchen. Flooring and cabinets damaged."},
    {"claim_id": "CLM-003", "policy": "HLTH-2024-9921", "type": "Medical", "amount": 42000, "status": "Pending Documents", "date": "2024-06-12", "description": "Emergency appendectomy at Apollo Hospital. Requesting pre-auth."},
]

class InsuranceClaimsAdapter(BaseAdapter):
    domain_name = "Insurance Claims Processing"
    system_prompt = """You are an intelligent insurance claims processing AI for TCS InsureAI Platform.

Capabilities:
- Validate policy coverage and check claim eligibility
- Assess submitted claims for completeness and accuracy
- Detect fraud patterns using behavioral and historical analysis
- Calculate preliminary settlement amounts based on policy terms
- Route complex claims requiring human adjuster review
- Ensure IRDAI regulatory compliance in all decisions

Response format: Always include Assessment, Required Documents (if any), Decision/Recommendation, and Timeline.
Be empathetic with claimants. Be precise with amounts and policy references."""

    kpi_definitions = {
        "auto_approval_rate": "% claims auto-approved without human review",
        "fraud_detection_rate": "% fraudulent claims correctly identified",
        "avg_processing_time_hrs": "Average hours from submission to decision",
        "customer_satisfaction": "CSAT score from post-claim surveys (1-5)",
        "cost_per_claim": "Average operational cost per claim processed",
    }
    suggested_tools = ["data_query_tool", "calculator_tool", "document_lookup_tool"]
    sample_questions = [
        "What is the current status of claim CLM-001?",
        "Analyze this damage photo and estimate repair cost",
        "Is policy COMP-2024-8823 eligible for this type of claim?",
        "Calculate settlement for auto accident with 40% depreciation on a 3-year-old vehicle worth ₹800,000",
        "This claim seems suspicious — check for fraud indicators",
    ]

    def get_config(self) -> dict:
        return {
            "domain": self.domain_name,
            "sample_data": SAMPLE_CLAIMS,
            "context": "\n".join(json.dumps(c) for c in SAMPLE_CLAIMS),
        }
