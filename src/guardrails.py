import json
from typing import Dict, Any, Tuple


# ==========================================
# 1. RISK CLASSIFICATION MATRIX
# ==========================================
def classify_action_risk(action_type: str, parameters: Dict[str, Any]) -> str:
    """
    Classifies operational actions by risk level: LOW, MEDIUM, HIGH.
    """
    act = action_type.lower()
    
    if act in ["read_metrics", "search_policy"]:
        return "LOW"
    
    if act == "calculate_incentive":
        total_cost = parameters.get("total_cost", 0.0)
        return "HIGH" if total_cost > 500.0 else "MEDIUM"
        
    if act == "trigger_surge_override":
        multiplier = parameters.get("new_multiplier", 1.0)
        if multiplier >= 1.3:
            return "HIGH"
        return "MEDIUM"
        
    return "HIGH"  # Default fallback for unknown actions


# ==========================================
# 2. INPUT GUARDRAILS
# ==========================================
def validate_input_parameters(airport_code: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Sanitizes and validates incoming operational parameters before processing.
    """
    valid_airports = ["SFO", "LAX", "JFK"]
    code = airport_code.strip().upper()
    
    if code not in valid_airports:
        return False, f"Invalid airport code '{airport_code}'. Supported: {valid_airports}"
        
    if "new_multiplier" in parameters:
        mult = parameters["new_multiplier"]
        if not isinstance(mult, (int, float)) or mult < 1.0 or mult > 2.5:
            return False, f"Surge multiplier {mult} out of bounds (1.0x - 2.5x)."
            
    if "driver_count" in parameters:
        count = parameters["driver_count"]
        if not isinstance(count, int) or count <= 0:
            return False, f"Driver count must be a positive integer. Got: {count}"
            
    return True, "Input validation passed."


# ==========================================
# 3. POLICY GUARDRAILS (HARD BOUNDARY ENFORCEMENT)
# ==========================================
def validate_policy_compliance(airport_code: str, proposed_surge: float) -> Tuple[bool, str]:
    """
    Hard policy boundary check independent of LLM reasoning.
    Max Caps: SFO = 1.5x, LAX = 1.8x, JFK = 1.6x.
    """
    code = airport_code.strip().upper()
    policy_caps = {
        "SFO": 1.5,
        "LAX": 1.8,
        "JFK": 1.6
    }
    
    max_cap = policy_caps.get(code, 1.5)
    
    if proposed_surge > max_cap:
        return False, f"POLICY VIOLATION: Proposed surge {proposed_surge}x exceeds maximum cap of {max_cap}x for {code}."
        
    return True, f"Policy check passed. Surge {proposed_surge}x within cap of {max_cap}x."


# ==========================================
# 4. HUMAN-IN-THE-LOOP (HITL) INTERCEPTOR
# ==========================================
def process_human_approval(action_summary: Dict[str, Any], human_decision: bool) -> Dict[str, Any]:
    """
    Processes human approval gate for HIGH risk actions.
    """
    risk_level = action_summary.get("risk_level", "HIGH")
    
    if risk_level != "HIGH":
        return {
            "status": "AUTO_EXECUTED",
            "approved": True,
            "message": "Action risk is LOW/MEDIUM. Executed automatically."
        }
        
    if human_decision is True:
        return {
            "status": "HUMAN_APPROVED_AND_EXECUTED",
            "approved": True,
            "message": f"Action approved by Operations Manager. Execution completed."
        }
    else:
        return {
            "status": "HUMAN_REJECTED",
            "approved": False,
            "message": f"Action REJECTED by Operations Manager. Execution aborted."
        }


if __name__ == "__main__":
    print("\n--- Testing Guardrails & HITL Standalone ---")
    
    # Test 1: Risk Classification
    print("Risk Surge 1.5x:", classify_action_risk("trigger_surge_override", {"new_multiplier": 1.5}))
    
    # Test 2: Input Validation
    print("Input Check Invalid:", validate_input_parameters("XYZ", {}))
    
    # Test 3: Policy Violation Check
    print("Policy Check SFO 2.0x:", validate_policy_compliance("SFO", 2.0))
    print("Policy Check SFO 1.4x:", validate_policy_compliance("SFO", 1.4))