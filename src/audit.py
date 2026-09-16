import json
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from src.config import BASE_DIR

OUTPUT_DIR = BASE_DIR / "output"
AUDIT_LOG_PATH = OUTPUT_DIR / "distilled_training_data.jsonl"


def ensure_output_directory():
    """Ensures the output directory exists."""
    if not OUTPUT_DIR.exists():
        os.makedirs(OUTPUT_DIR, exist_ok=True)


def log_interaction_event(
    query: str,
    airport_code: str,
    investigation: Dict[str, Any],
    policy_evaluation: Dict[str, Any],
    recommendation: Dict[str, Any],
    risk_level: str,
    human_approval_status: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Formats end-to-end execution state into a structured schema
    and appends it to a JSONL file for audit trail and dataset distillation.
    """
    ensure_output_directory()
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    record = {
        "timestamp": timestamp,
        "query": query,
        "airport_code": airport_code,
        "risk_level": risk_level,
        "investigation_summary": {
            "is_anomaly": investigation.get("is_anomaly", False),
            "severity": investigation.get("severity", "LOW"),
            "contributing_factors": investigation.get("contributing_factors", [])
        },
        "policy_evaluation": {
            "sources": policy_evaluation.get("sources", []),
            "proposed_action": policy_evaluation.get("proposed_action", ""),
            "llm_evaluation": policy_evaluation.get("llm_evaluation", "")
        },
        "recommendation": recommendation.get("recommendation", ""),
        "human_approval_status": human_approval_status,
        "distillation_prompt": f"User: {query}\nAirport: {airport_code}",
        "distillation_completion": recommendation.get("recommendation", "")
    }
    
    # Write record to JSONL file
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
        
    print(f"[Audit Manager] Event logged successfully to '{AUDIT_LOG_PATH}'.")
    return record


if __name__ == "__main__":
    print("\n--- Testing Audit Logging Standalone ---")
    mock_log = log_interaction_event(
        query="Mock test query",
        airport_code="SFO",
        investigation={"is_anomaly": True, "severity": "HIGH"},
        policy_evaluation={"sources": ["sfo_pricing.txt"]},
        recommendation={"recommendation": "Increase surge to 1.4x"},
        risk_level="HIGH",
        human_approval_status={"status": "HUMAN_APPROVED_AND_EXECUTED", "approved": True}
    )
    print("Mock Record Created Timestamp:", mock_log["timestamp"])