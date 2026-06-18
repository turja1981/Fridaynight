from adapters.base import BaseAdapter

class ManufacturingAdapter(BaseAdapter):
    domain_name = "Manufacturing Quality Control"
    system_prompt = """You are a quality control AI for TCS ManufactureAI Platform.
Responsibilities: defect detection, root cause analysis, process optimization, ISO 9001 compliance.
Always reference batch IDs and equipment numbers. Be data-driven."""
    kpi_definitions = {
        "defect_detection_rate": "% defects caught by AI vs total defects",
        "quality_score": "Overall quality score out of 100",
        "downtime_reduction": "% reduction in unplanned downtime",
        "yield_rate": "% of production meeting quality standards",
    }
    sample_questions = [
        "Analyze this product image for defects",
        "Batch B-2024-441 has 8% defect rate — root cause analysis?",
        "Generate quality report for shift 2 production",
    ]
    def get_config(self) -> dict:
        return {"domain": self.domain_name, "sample_data": [], "context": "Manufacturing quality context."}
