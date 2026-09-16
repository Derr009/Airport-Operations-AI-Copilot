import pytest
from src.tools import get_airport_metrics, calculate_driver_incentive, trigger_surge_override
from src.tool_calling import run_tool_calling_workflow


def test_get_airport_metrics_valid():
    res = get_airport_metrics("SFO")
    assert "error" not in res
    assert res["airport_code"] == "SFO"
    assert res["completion_rate"] == 0.71


def test_get_airport_metrics_invalid():
    res = get_airport_metrics("INVALID_CODE")
    assert "error" in res


def test_calculate_driver_incentive():
    res = calculate_driver_incentive(20, "high")
    assert res["per_trip_bonus"] == 10.0
    assert res["total_cost"] == 200.0
    assert res["status"] == "APPROVED"


def test_tool_calling_agent_intent():
    res = run_tool_calling_workflow("What is the average ETA and queue size at SFO right now?")
    assert "get_airport_metrics" in res["executed_tools"]
    assert len(res["tool_outputs"]) > 0
    assert "18.5" in res["final_response"] or "18" in res["final_response"]


def run_all_tool_tests():
    print("\n==========================================")
    print("      RUNNING DAY 2 TOOL TEST SUITE       ")
    print("==========================================\n")
    
    tests = [
        ("Direct Tool: SFO Metrics", test_get_airport_metrics_valid),
        ("Direct Tool: Invalid Airport Code", test_get_airport_metrics_invalid),
        ("Direct Tool: Incentive Calculation", test_calculate_driver_incentive),
        ("LLM Tool Calling: SFO ETA Query", test_tool_calling_agent_intent),
    ]
    
    passed = 0
    for name, test_func in tests:
        try:
            test_func()
            print(f" {name}: PASSED")
            passed += 1
        except AssertionError as e:
            print(f" {name}: FAILED - {str(e)}")
        except Exception as e:
            print(f" {name}: ERROR - {str(e)}")

    print("\n------------------------------------------")
    print(f"Test Score: {passed}/{len(tests)} passed.")
    if passed == len(tests):
        print("Success Criteria Met! All operational tool tests passed. ")
    print("------------------------------------------\n")


if __name__ == "__main__":
    run_all_tool_tests()