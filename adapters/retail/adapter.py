from __future__ import annotations
import json

from adapters.base import BaseAdapter

_SAMPLE_PRODUCTS = [
    {"id": "P-001", "name": "Laptop Pro 15", "category": "Electronics", "price": 85000, "stock": 42, "rating": 4.5, "tags": ["laptop", "work", "premium"]},
    {"id": "P-002", "name": "Wireless Headphones X3", "category": "Electronics", "price": 8999, "stock": 156, "rating": 4.3, "tags": ["audio", "wireless", "music"]},
    {"id": "P-003", "name": "Running Shoes Pro", "category": "Sports", "price": 4500, "stock": 89, "rating": 4.7, "tags": ["sports", "running", "fitness"]},
    {"id": "P-004", "name": "Smart Watch Series 5", "category": "Electronics", "price": 22000, "stock": 34, "rating": 4.4, "tags": ["smartwatch", "fitness", "tech"]},
]


class RetailAdapter(BaseAdapter):
    """Adapter for Retail Customer Experience and Product Recommendations domain."""

    domain_name = "Retail & E-Commerce"

    system_prompt = (
        "You are an expert Retail AI Assistant for EnterpriseMart, India's leading e-commerce platform. "
        "Your core responsibilities:\n"
        "1. PRODUCT RECOMMENDATIONS: Provide personalized product suggestions based on preferences and history\n"
        "2. ORDER MANAGEMENT: Help track orders, process returns, handle delivery issues\n"
        "3. CUSTOMER SUPPORT: Resolve complaints, answer product queries, handle refunds\n"
        "4. INVENTORY QUERIES: Check stock availability, notify about restocking\n"
        "5. PROMOTIONS: Inform customers about relevant deals, coupons, and offers\n\n"
        "Guidelines:\n"
        "- Always be friendly and customer-centric\n"
        "- Prioritize customer satisfaction over short-term sales\n"
        "- Follow consumer protection regulations\n"
        "- Recommend complementary products (upsell) naturally, not aggressively"
    )

    kpi_definitions = {
        "recommendation_ctr": "Click-through rate on AI recommendations (target: >15%)",
        "conversion_rate": "Percentage of AI-assisted sessions leading to purchase (target: >10%)",
        "avg_basket_size_increase": "Multiplier improvement in basket size from recommendations (target: >1.2x)",
        "customer_retention_rate": "Percentage of customers who return within 30 days (target: >75%)",
    }

    suggested_tools = ["data_query", "document_lookup", "web_search", "calculator"]

    sample_questions = [
        "Can you recommend a laptop for video editing under ₹90,000?",
        "Where is my order #ORD-2024-88765?",
        "I want to return a product I bought last week",
        "What are the best-selling electronics this month?",
        "Do you have wireless headphones in stock?",
        "Apply coupon code SAVE20 to my cart",
    ]

    def get_config(self) -> dict:
        """Return retail adapter configuration."""
        return {
            "domain_name": self.domain_name,
            "system_prompt": self.system_prompt,
            "kpi_definitions": self.kpi_definitions,
            "suggested_tools": self.suggested_tools,
            "sample_questions": self.sample_questions,
        }

    def get_sample_context(self) -> str:
        """Return sample product catalog as context."""
        return (
            f"Product Catalog — {len(_SAMPLE_PRODUCTS)} products available:\n\n"
            + json.dumps(_SAMPLE_PRODUCTS, indent=2)
        )
