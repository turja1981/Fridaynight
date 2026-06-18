from __future__ import annotations
import json

from adapters.base import BaseAdapter

_SAMPLE_ACCOUNTS = [
    {
        "account_id": "ACC-2024-001",
        "customer": "Rahul Verma",
        "account_type": "Savings",
        "balance": 245670.50,
        "status": "Active",
        "recent_transactions": [
            {"date": "2024-03-15", "type": "debit", "amount": 15000, "merchant": "Amazon", "flagged": False},
            {"date": "2024-03-14", "type": "credit", "amount": 80000, "source": "Salary", "flagged": False},
            {"date": "2024-03-13", "type": "debit", "amount": 95000, "merchant": "Unknown", "flagged": True},
        ],
    },
    {
        "account_id": "ACC-2024-002",
        "customer": "Meena Krishnamurthy",
        "account_type": "Current",
        "balance": 1250000.00,
        "status": "Active",
        "recent_transactions": [
            {"date": "2024-03-15", "type": "debit", "amount": 500000, "merchant": "Wire Transfer", "flagged": True},
        ],
    },
]


class BankingAdapter(BaseAdapter):
    """Adapter for Banking Customer Service and Fraud Detection domain."""

    domain_name = "Banking & Financial Services"

    system_prompt = (
        "You are an expert Banking AI Assistant for Enterprise National Bank. "
        "Your core responsibilities:\n"
        "1. CUSTOMER SERVICE: Handle account queries, balance checks, transaction history\n"
        "2. FRAUD DETECTION: Identify suspicious transactions using pattern analysis\n"
        "3. KYC/AML COMPLIANCE: Verify customer identity and flag suspicious activity\n"
        "4. PRODUCT RECOMMENDATIONS: Suggest appropriate banking products based on customer profile\n"
        "5. DISPUTE RESOLUTION: Handle transaction disputes and chargebacks\n\n"
        "Guidelines:\n"
        "- Verify identity before sharing account details\n"
        "- Immediately flag transactions >₹100,000 to a different account as HIGH RISK\n"
        "- Follow RBI guidelines for all operations\n"
        "- Never share CVV, OTP, or full card numbers"
    )

    kpi_definitions = {
        "query_resolution_rate": "Percentage of customer queries resolved without escalation (target: >85%)",
        "escalation_rate": "Percentage of cases requiring human agent (target: <15%)",
        "avg_response_time": "Average time to respond to customer query in ms (target: <500ms)",
        "fraud_alerts_generated": "Number of fraud alerts raised per day",
        "nps_score": "Net Promoter Score from customer surveys (target: >50)",
    }

    suggested_tools = ["data_query", "calculator", "document_lookup", "datetime_tool"]

    sample_questions = [
        "What is my current account balance?",
        "Show me my last 5 transactions",
        "I see a suspicious transaction on my account",
        "How do I apply for a home loan?",
        "What are the current FD interest rates?",
        "Block my debit card immediately",
    ]

    def get_config(self) -> dict:
        """Return banking adapter configuration."""
        return {
            "domain_name": self.domain_name,
            "system_prompt": self.system_prompt,
            "kpi_definitions": self.kpi_definitions,
            "suggested_tools": self.suggested_tools,
            "sample_questions": self.sample_questions,
        }

    def get_sample_context(self) -> str:
        """Return sample banking data as context."""
        return (
            f"Banking System — {len(_SAMPLE_ACCOUNTS)} accounts loaded:\n\n"
            + json.dumps(_SAMPLE_ACCOUNTS, indent=2)
        )
