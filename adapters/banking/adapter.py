from adapters.base import BaseAdapter

class BankingAdapter(BaseAdapter):
    domain_name = "Banking Customer Service"
    system_prompt = """You are an intelligent banking assistant for TCS BankAI Platform.
Responsibilities: account inquiries, fraud detection, loan assessment, RBI compliance.
Always verify identity before sharing account details. Flag suspicious transactions immediately."""
    kpi_definitions = {
        "query_resolution_rate": "% queries resolved without human escalation",
        "fraud_alerts_caught": "% fraudulent transactions flagged correctly",
        "avg_response_time": "Average response time in seconds",
        "customer_nps": "Net Promoter Score from interactions",
    }
    sample_questions = [
        "Check transaction TXN-001 for fraud indicators",
        "What are the current home loan interest rates?",
        "My account shows an unauthorized transaction of ₹45,000",
    ]
    def get_config(self) -> dict:
        return {"domain": self.domain_name, "sample_data": [], "context": "Banking domain context."}
