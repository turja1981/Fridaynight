from __future__ import annotations
import json

from adapters.base import BaseAdapter

_SAMPLE_INSPECTION_DATA = [
    {
        "batch_id": "BATCH-2024-0315-A",
        "product": "Electronic PCB Module",
        "line": "Line-3",
        "total_units": 500,
        "inspected": 500,
        "passed": 487,
        "failed": 13,
        "defect_types": {"solder_bridge": 6, "missing_component": 4, "crack": 3},
        "defect_rate": 0.026,
        "timestamp": "2024-03-15T09:30:00Z",
    },
    {
        "batch_id": "BATCH-2024-0315-B",
        "product": "Automotive Brake Pad",
        "line": "Line-7",
        "total_units": 1000,
        "inspected": 1000,
        "passed": 998,
        "failed": 2,
        "defect_types": {"thickness_variance": 2},
        "defect_rate": 0.002,
        "timestamp": "2024-03-15T11:00:00Z",
    },
]


class ManufacturingAdapter(BaseAdapter):
    """Adapter for Manufacturing Quality Control and Defect Analysis domain."""

    domain_name = "Manufacturing Quality Control"

    system_prompt = (
        "You are an expert Manufacturing AI Quality Control System for EnterpriseMfg Corp. "
        "Your core responsibilities:\n"
        "1. DEFECT DETECTION: Analyze product images and sensor data to identify defects\n"
        "2. ROOT CAUSE ANALYSIS: Identify underlying causes of quality issues\n"
        "3. PROCESS OPTIMIZATION: Recommend adjustments to reduce defect rates\n"
        "4. PREDICTIVE MAINTENANCE: Flag equipment likely to cause quality issues\n"
        "5. COMPLIANCE REPORTING: Generate ISO 9001 compliant quality reports\n\n"
        "Guidelines:\n"
        "- Use Six Sigma methodology (DMAIC) for problem solving\n"
        "- Reference control charts for statistical process control\n"
        "- Classify defects as: Critical (safety risk), Major (functional), Minor (cosmetic)\n"
        "- Trigger line stoppage if defect rate exceeds 5%"
    )

    kpi_definitions = {
        "defect_detection_rate": "Percentage of actual defects correctly identified by AI (target: >95%)",
        "quality_score": "Overall product quality score 0-100 (target: >97)",
        "inspection_time_reduction": "Time saved vs manual inspection (target: >60%)",
        "false_positive_rate": "Good products incorrectly rejected (target: <3%)",
    }

    suggested_tools = ["document_lookup", "calculator", "data_query"]

    sample_questions = [
        "What is the defect rate for Batch BATCH-2024-0315-A?",
        "Analyze this PCB image for defects",
        "Which production line has the highest defect rate this week?",
        "Generate a quality report for today's production",
        "What is the root cause of solder bridge defects?",
        "Should we stop Line-3 based on current defect rates?",
    ]

    def get_config(self) -> dict:
        """Return manufacturing adapter configuration."""
        return {
            "domain_name": self.domain_name,
            "system_prompt": self.system_prompt,
            "kpi_definitions": self.kpi_definitions,
            "suggested_tools": self.suggested_tools,
            "sample_questions": self.sample_questions,
        }

    def get_sample_context(self) -> str:
        """Return sample inspection data as context."""
        return (
            f"Manufacturing QC System — {len(_SAMPLE_INSPECTION_DATA)} recent batches:\n\n"
            + json.dumps(_SAMPLE_INSPECTION_DATA, indent=2)
        )
