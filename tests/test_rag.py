import pytest
from src.policy_qa import answer_policy_question

TEST_QUESTIONS = [
    {
        "question": "What is the maximum surge multiplier allowed at SFO?",
        "expected_source": "sfo_pricing.txt",
        "keywords": ["1.5x", "maximum"]
    },
    {
        "question": "Can drivers abandon the airport queue at SFO?",
        "expected_source": "sfo_operations.txt",
        "keywords": ["5 minutes", "forfeits", "abandonment"]
    },
    {
        "question": "What approval is required before increasing surge at SFO above 1.3x?",
        "expected_source": "sfo_pricing.txt",
        "keywords": ["Human Operations Manager Approval", "1.3x"]
    },
    {
        "question": "Where is the designated staging area for LAX drivers?",
        "expected_source": "lax_operations.txt",
        "keywords": ["LAX-it", "6100 W 98th St"]
    },
    {
        "question": "What is the maximum staging queue capacity at JFK?",
        "expected_source": "jfk_operations.txt",
        "keywords": ["250", "active vehicles"]
    }
]


def run_rag_tests():
    print("\n==========================================")
    print("      RUNNING DAY 1 RAG TEST SUITE       ")
    print("==========================================\n")
    
    passed = 0
    
    for i, test in enumerate(TEST_QUESTIONS, 1):
        print(f"Test {i}: {test['question']}")
        result = answer_policy_question(test["question"])
        
        answer = result["answer"]
        sources = result["sources"]
        
        # Verify source matching
        source_matched = test["expected_source"] in sources
        
        print(f"  Resulting Answer: {answer}")
        print(f"  Sources Found: {sources}")
        
        if source_matched:
            print("  Status: PASSED \n")
            passed += 1
        else:
            print(f"  Status: FAILED  (Expected source: {test['expected_source']})\n")
            
    print("------------------------------------------")
    print(f"Test Score: {passed}/{len(TEST_QUESTIONS)} passed.")
    if passed >= 4:
        print("Success Criteria Met! (At least 4/5 passed) ")
    else:
        print("Success Criteria Not Met. Retrying chunking or embeddings needed.")
    print("------------------------------------------\n")


if __name__ == "__main__":
    run_rag_tests()