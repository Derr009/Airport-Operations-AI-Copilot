import pytest
from src.agents import run_investigator_agent
from src.orchestrator import OperationsOrchestrator


def test_investigator_anomaly_detection():
    """Verify Investigator flags SFO completion rate drop (< 85%)."""
    res = run_investigator_agent("SFO")
    assert res["is_anomaly"] is True
    assert res["severity"] in ["MEDIUM", "HIGH"]
    assert "completion_rate" in res["metrics"]


def test_orchestrator_end_to_end():
    """Verify full end-to-end multi-agent execution loop."""
    orchestrator = OperationsOrchestrator()
    res = orchestrator.process_query("Investigate SFO airport operations.")
    
    assert res["airport_code"] == "SFO"
    assert "execution_trace" in res
    assert len(res["execution_trace"]) == 3
    assert res["resolution"]["status"] == "RECOMMENDATION_GENERATED"


def run_agent_tests():
    print("\n==========================================")
    print("      RUNNING DAY 3 AGENT TEST SUITE      ")
    print("==========================================\n")
    
    tests = [
        ("Standalone Investigator Agent", test_investigator_anomaly_detection),
        ("Orchestrator Multi-Agent Loop", test_orchestrator_end_to_end),
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
    run_agent_tests()