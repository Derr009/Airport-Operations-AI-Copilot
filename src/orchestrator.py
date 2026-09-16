import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from src.memory import ConversationMemory
from src.agents import (
    run_investigator_agent,
    run_policy_agent,
    run_resolution_agent
)
from src.guardrails import (
    classify_action_risk,
    validate_input_parameters,
    validate_policy_compliance,
    process_human_approval
)
from src.audit import log_interaction_event

load_dotenv()


class SecureOperationsOrchestrator:
    """
    Multi-Agent Orchestrator augmented with Day 4 Guardrails, HITL Interceptors,
    and Distillation Audit Logging.
    """
    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations
        self.memory = ConversationMemory()

    def _extract_airport_code(self, query: str) -> str:
        """Extracts airport code from query or memory context."""
        query_upper = query.upper()
        for code in ["SFO", "LAX", "JFK"]:
            if code in query_upper:
                self.memory.update_active_airport(code)
                return code
            
        if self.memory.active_airport:
            return self.memory.active_airport
            
        return "SFO"

    def process_query_with_safety(
        self,
        user_query: str,
        target_proposed_surge: Optional[float] = 1.4,
        human_decision: bool = True
    ) -> Dict[str, Any]:
        """
        Executes end-to-end safe multi-agent loop:
        1. Input Guardrails
        2. Investigator Agent
        3. Policy Agent & Hard Bounds Validation
        4. Resolution Agent
        5. Risk Classification & HITL Approval
        6. Audit Logging
        """
        print(f"\n==========================================")
        print(f"  SAFE ORCHESTRATOR: Processing Query    ")
        print(f"==========================================")
        print(f"User Query: '{user_query}'")
        
        airport_code = self._extract_airport_code(user_query)
        self.memory.add_message("user", user_query)
        
        # 1. Input Guardrails Check
        input_valid, input_msg = validate_input_parameters(airport_code, {"new_multiplier": target_proposed_surge})
        if not input_valid:
            print(f" Guardrail Rejection: {input_msg}")
            return {"error": input_msg, "status": "GUARDRAIL_REJECTED"}
        
        # 2. Investigator Agent Execution
        print(f"\n[Step 1/3] Telemetry Investigation for {airport_code}...")
        investigation = run_investigator_agent(airport_code)
        
        # 3. Hard Policy Compliance Guardrail Check
        policy_valid, policy_msg = validate_policy_compliance(airport_code, target_proposed_surge)
        print(f"[Policy Guardrail Check] {policy_msg}")
        
        if not policy_valid:
            return {
                "error": policy_msg,
                "status": "POLICY_VIOLATION_BLOCKED",
                "investigation": investigation
            }

        # 4. Policy Agent RAG Analysis
        print(f"\n[Step 2/3] Policy & Compliance Check...")
        proposed_action = f"Set surge multiplier for {airport_code} to {target_proposed_surge}x."
        policy_eval = run_policy_agent(airport_code, proposed_action)
        
        # 5. Resolution Agent Recommendation
        print(f"\n[Step 3/3] Resolution Agent Synthesis...")
        resolution = run_resolution_agent(investigation, policy_eval)
        
        # 6. Risk Classification & Human-in-the-Loop Interceptor
        action_params = {"new_multiplier": target_proposed_surge}
        risk_level = classify_action_risk("trigger_surge_override", action_params)
        print(f"\n[Risk Governance] Action Risk Level: {risk_level}")
        
        approval_result = process_human_approval(
            {"risk_level": risk_level, "action": proposed_action},
            human_decision=human_decision
        )
        print(f"[HITL Status] {approval_result['status']}: {approval_result['message']}")
        
        # 7. Audit & Distillation Logging
        audit_record = log_interaction_event(
            query=user_query,
            airport_code=airport_code,
            investigation=investigation,
            policy_evaluation=policy_eval,
            recommendation=resolution,
            risk_level=risk_level,
            human_approval_status=approval_result
        )
        
        final_response_text = resolution["recommendation"]
        self.memory.add_message("assistant", final_response_text)
        
        return {
            "query": user_query,
            "airport_code": airport_code,
            "risk_level": risk_level,
            "policy_guardrail": policy_msg,
            "investigation": investigation,
            "policy_evaluation": policy_eval,
            "resolution": resolution,
            "hitl_approval": approval_result,
            "audit_logged": True
        }