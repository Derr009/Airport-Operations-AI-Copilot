import pytest
from src.guardrails import (
    classify_action_risk,
    validate_input_parameters,
    validate_policy_compliance,
    process_human_approval
)


def test_input_validation_invalid_airport():
    valid, msg = validate_input_parameters("INVALID", {})
    assert valid is False
    assert "Invalid airport code" in msg


def test_input_validation_out_of_bounds_surge():
    valid, msg = validate_input_parameters("SFO", {"new_multiplier": 4.5})
    assert valid is False
    assert "out of bounds" in msg


def test_policy_compliance_surge_over_cap():
    """Verify SFO cap of 1.5x blocks a 2.0x surge attempt."""
    valid, msg = validate_policy_compliance("SFO", 2.0)
    assert valid is False
    assert "POLICY VIOLATION" in msg


def test_policy_compliance_surge_within_cap():
    """Verify SFO cap of 1.5x allows a 1.4x surge attempt."""
    valid, msg = validate_policy_compliance("SFO", 1.4)
    assert valid is True


def test_risk_classification_surge():
    risk_high = classify_action_risk("trigger_surge_override", {"new_multiplier": 1.4})
    assert risk_high == "HIGH"
    
    risk_med = classify_action_risk("trigger_surge_override", {"new_multiplier": 1.1})
    assert risk_med == "MEDIUM"


def test_hitl_approval_approved():
    res = process_human_approval({"risk_level": "HIGH"}, human_decision=True)
    assert res["approved"] is True
    assert res["status"] == "HUMAN_APPROVED_AND_EXECUTED"


def test_hitl_approval_rejected():
    res = process_human_approval({"risk_level": "HIGH"}, human_decision=False)
    assert res["approved"] is False
    assert res["status"] == "HUMAN_REJECTED"


def run_guardrail_tests():
    print("\n==========================================")
    print("    RUNNING DAY 4 GUARDRAIL TEST SUITE    ")
    print("==========================================\n")
    
    tests = [
        ("Input Guardrail: Invalid Airport", test_input_validation_invalid_airport),
        ("Input Guardrail: Out of Bounds Surge", test_input_validation_out_of_bounds_surge),
        ("Policy Guardrail: Block Over-Cap Surge", test_policy_compliance_surge_over_cap),
        ("Policy Guardrail: Allow Within-Cap Surge", test_policy_compliance_surge_within_cap),
        ("Risk Governance Matrix", test_risk_classification_surge),
        ("HITL Gate: Human Approved", test_hitl_approval_approved),
        ("HITL Gate: Human Rejected", test_hitl_approval_rejected),
    ]
    
    passed = 0
    for name, test_func in tests:
        try:
            test_func()
            print(f" {name}: PASSED")
            passed += 1
        except Exception as e:
            print(f" {name}: FAILED - {str(e)}")

    print("\n------------------------------------------")
    print(f"Test Score: {passed}/{len(tests)} passed.")
    print("------------------------------------------\n")


if __name__ == "__main__":
    run_guardrail_tests()