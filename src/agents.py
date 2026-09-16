import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.tools import get_airport_metrics, calculate_driver_incentive
from src.policy_qa import answer_policy_question

load_dotenv()


def get_agent_llm():
    """Returns a deterministic LLM instance for multi-agent reasoning."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY in .env file.")
    
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.0,
        google_api_key=api_key
    )


# ==========================================
# AGENT 1: OPERATIONS INVESTIGATOR AGENT
# ==========================================
def run_investigator_agent(airport_code: str) -> Dict[str, Any]:
    """
    Analyzes airport telemetry, detects anomalies against operational thresholds,
    and isolates contributing factors.
    """
    print(f"\n[Agent: Operations Investigator] Inspecting telemetry for {airport_code}...")
    
    # Fetch live telemetry metrics using Day 2 tool
    metrics = get_airport_metrics(airport_code)
    
    if "error" in metrics:
        return {"status": "FAILED", "error": metrics["error"]}
    
    completion_rate = metrics.get("completion_rate", 1.0)
    cancellation_rate = metrics.get("driver_cancellation_rate", 0.0)
    eta = metrics.get("average_eta", 0.0)
    queue_size = metrics.get("queue_size", 0)
    
    # Operational Baselines
    # Completion Rate < 85% is flagged as ANOMALY
    is_anomaly = completion_rate < 0.85
    
    contributing_factors = []
    if cancellation_rate > 0.15:
        contributing_factors.append(f"High driver cancellation rate ({cancellation_rate * 100:.1f}%)")
    if eta > 15.0:
        contributing_factors.append(f"Elevated average ETA ({eta} mins)")
    if queue_size > 150:
        contributing_factors.append(f"Large airport queue ({queue_size} vehicles)")
        
    severity = "HIGH" if completion_rate < 0.75 else ("MEDIUM" if is_anomaly else "LOW")
    
    investigation_summary = {
        "airport_code": airport_code,
        "metrics": metrics,
        "is_anomaly": is_anomaly,
        "severity": severity,
        "issue_description": f"Completion rate ({completion_rate * 100:.1f}%) is below target threshold (>85%)." if is_anomaly else "Operations operating within normal thresholds.",
        "contributing_factors": contributing_factors
    }
    
    return investigation_summary


# ==========================================
# AGENT 2: POLICY & COMPLIANCE AGENT
# ==========================================
def run_policy_agent(airport_code: str, proposed_action: str) -> Dict[str, Any]:
    """
    Queries ChromaDB RAG store to evaluate policy rules and check if
    proposed intervention complies with airport regulations.
    """
    print(f"\n[Agent: Policy & Compliance] Checking RAG policies for {airport_code}...")
    
    query = f"What is the maximum surge multiplier and pricing policy rules allowed for {airport_code}?"
    rag_result = answer_policy_question(query)
    
    policy_text = rag_result["answer"]
    sources = rag_result["sources"]
    
    # Query LLM for compliance check
    llm = get_agent_llm()
    prompt = f"""
You are the Policy & Compliance Agent. 
Evaluated Airport: {airport_code}
Proposed Operational Action: {proposed_action}

Retrieved Airport Policies:
{policy_text}

Task:
Determine if the proposed action is compliant with airport regulations.
Identify specific policy limits (e.g. max surge caps, approval requirements).

Return your evaluation in JSON format:
{{
  "is_compliant": true/false,
  "max_allowed_surge": float or null,
  "approval_required": true/false,
  "policy_summary": "Brief summary of rule"
}}
"""
    response = llm.invoke(prompt)
    content = response.content if isinstance(response.content, str) else str(response.content)
    
    return {
        "airport_code": airport_code,
        "proposed_action": proposed_action,
        "policy_text": policy_text,
        "sources": sources,
        "llm_evaluation": content
    }


# ==========================================
# AGENT 3: RESOLUTION AGENT
# ==========================================
def run_resolution_agent(investigation: Dict[str, Any], policy_evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes telemetry anomaly data and policy constraints into a structured,
    actionable recommendation list.
    """
    print(f"\n[Agent: Resolution Agent] Synthesizing operational recommendation...")
    
    llm = get_agent_llm()
    prompt = f"""
You are the Resolution Agent. Synthesize the findings into a clear operational recommendation.

Investigation Findings:
{json.dumps(investigation, indent=2)}

Policy & Compliance Check:
{json.dumps(policy_evaluation, indent=2)}

Generate a structured response with:
1. Operational Assessment
2. Recommended Action Plan (Step-by-step)
3. Governance / Risk Level (Low, Medium, or High)
"""
    response = llm.invoke(prompt)
    recommendation_text = response.content if isinstance(response.content, str) else str(response.content)
    
    return {
        "recommendation": recommendation_text,
        "status": "RECOMMENDATION_GENERATED"
    }


if __name__ == "__main__":
    print("--- Testing Individual Specialized Agents ---")
    
    # 1. Test Investigator
    inv_res = run_investigator_agent("SFO")
    print("\nInvestigator Result:\n", json.dumps(inv_res, indent=2))
    
    # 2. Test Policy
    pol_res = run_policy_agent("SFO", "Increase surge to 1.5x")
    print("\nPolicy Agent Result:\n", json.dumps(pol_res, indent=2))