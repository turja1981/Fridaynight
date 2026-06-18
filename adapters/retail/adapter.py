from adapters.base import BaseAdapter

class RetailAdapter(BaseAdapter):
    domain_name = "Retail Customer Experience"
    system_prompt = """You are a retail AI assistant for TCS RetailAI Platform.
Responsibilities: personalized recommendations, complaint resolution, order tracking, loyalty programs.
Be warm, helpful, and focused on customer retention."""
    kpi_definitions = {
        "recommendation_accuracy": "% of recommendations resulting in purchase",
        "cart_conversion": "% of assisted sessions converting to purchase",
        "support_resolution_time": "Average minutes to resolve support ticket",
        "nps_score": "Net Promoter Score",
    }
    sample_questions = [
        "Recommend products for a customer who bought running shoes last month",
        "Customer complaint: order ORD-8821 arrived damaged",
        "Analyze customer sentiment from these 10 reviews",
    ]
    def get_config(self) -> dict:
        return {"domain": self.domain_name, "sample_data": [], "context": "Retail customer experience context."}
