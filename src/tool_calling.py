import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import StructuredTool

from src.tools import (
    get_airport_metrics,
    calculate_driver_incentive,
    trigger_surge_override
)

load_dotenv()

# 1. Wrap custom functions as LangChain StructuredTools
tools = [
    StructuredTool.from_function(
        func=get_airport_metrics,
        name="get_airport_metrics",
        description="Fetch real-time operational telemetry for an airport code ('SFO', 'LAX', 'JFK')."
    ),
    StructuredTool.from_function(
        func=calculate_driver_incentive,
        name="calculate_driver_incentive",
        description="Calculate driver incentive costs given driver_count (int) and severity_level ('low' or 'high')."
    ),
    StructuredTool.from_function(
        func=trigger_surge_override,
        name="trigger_surge_override",
        description="Prepare a surge override for an airport code, new_multiplier (float), and operational reason."
    )
]

# Map tool names to actual callable Python functions
TOOL_MAP = {
    "get_airport_metrics": get_airport_metrics,
    "calculate_driver_incentive": calculate_driver_incentive,
    "trigger_surge_override": trigger_surge_override
}


def get_llm_with_tools():
    """Initializes LLM bound with operational tools."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY in .env file.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.0,
        google_api_key=api_key
    )
    return llm.bind_tools(tools)


def run_tool_calling_workflow(user_query: str) -> Dict[str, Any]:
    """
    Executes function-calling flow:
    Query -> LLM Decision -> Tool Execution -> Results Synthesis
    """
    llm = get_llm_with_tools()
    
    # 1. First pass: LLM determines if tool call is required
    response = llm.invoke(user_query)
    
    executed_tools = []
    tool_outputs = []

    # Check for tool call requests
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            executed_tools.append(tool_name)
            
            print(f"-> Agent invoked tool '{tool_name}' with args: {tool_args}")
            
            # Execute tool safely
            if tool_name in TOOL_MAP:
                try:
                    tool_result = TOOL_MAP[tool_name](**tool_args)
                except Exception as e:
                    tool_result = {"error": f"Tool execution failed: {str(e)}"}
            else:
                tool_result = {"error": f"Tool '{tool_name}' not found."}

            tool_outputs.append({
                "tool": tool_name,
                "args": tool_args,
                "result": tool_result
            })

        # 2. Second pass: Generate final response using tool output context
        synthesis_prompt = f"""
User Query: {user_query}

Tool Execution Results:
{json.dumps(tool_outputs, indent=2)}

Synthesize a clear, concise operational response based strictly on the tool output results.
"""
        final_response = llm.invoke(synthesis_prompt)
        final_text = final_response.content if isinstance(final_response.content, str) else str(final_response.content)
    else:
        # Direct textual response (no tool call was needed)
        final_text = response.content if isinstance(response.content, str) else str(response.content)

    return {
        "query": user_query,
        "executed_tools": executed_tools,
        "tool_outputs": tool_outputs,
        "final_response": final_text
    }


if __name__ == "__main__":
    print("\n--- Testing Function Calling Workflow ---\n")
    
    # Test 1: Query requiring metrics tool
    q1 = "What is currently happening at SFO airport?"
    print(f"Query 1: '{q1}'")
    res1 = run_tool_calling_workflow(q1)
    print("Final Answer:\n", res1["final_response"])
    print("\n" + "="*50 + "\n")
    
    # Test 2: Error handling for invalid airport code
    q2 = "Get operational metrics for XYZ airport."
    print(f"Query 2: '{q2}'")
    res2 = run_tool_calling_workflow(q2)
    print("Final Answer:\n", res2["final_response"])