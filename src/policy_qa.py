import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from src.vector_store import query_vector_store
from src.prompts import SYSTEM_POLICY_QA_PROMPT
from src.config import TOP_K_RESULTS

load_dotenv()


def get_llm():
    """Initializes the Gemini LLM instance."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY in .env file.")
    
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.0,
        google_api_key=api_key
    )


def parse_response_content(content: Any) -> str:
    """Safely extracts text string from LLM response content."""
    if isinstance(content, str):
        return content.strip()
    elif isinstance(content, list):
        # Extract text elements if content is returned as a list of parts
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif hasattr(part, "text"):
                text_parts.append(part.text)
        return "\n".join(text_parts).strip()
    return str(content).strip()


def answer_policy_question(query: str, top_k: int = TOP_K_RESULTS) -> Dict[str, Any]:
    """
    Executes complete RAG pipeline:
    User Query -> Search ChromaDB -> Construct Context -> LLM Generation -> Answer + Sources
    """
    # 1. Retrieve relevant chunks
    retrieved_docs = query_vector_store(query, top_k=top_k)
    
    if not retrieved_docs:
        return {
            "answer": "No relevant policy documents were found.",
            "sources": []
        }
    
    # 2. Extract unique source file names
    sources = list(set(doc.metadata.get("source", "Unknown") for doc in retrieved_docs))
    
    # 3. Format context string with source attribution
    context_str = "\n\n".join([
        f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}"
        for doc in retrieved_docs
    ])
    
    # 4. Build Prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_POLICY_QA_PROMPT),
        ("user", "User Question: {question}")
    ])
    
    llm = get_llm()
    chain = prompt_template | llm
    
    # 5. Generate Response
    response = chain.invoke({
        "context": context_str,
        "question": query
    })
    
    clean_answer = parse_response_content(response.content)
    
    return {
        "answer": clean_answer,
        "sources": sources,
        "retrieved_chunks": [doc.page_content for doc in retrieved_docs]
    }


if __name__ == "__main__":
    # Test Policy Q&A Script
    test_query = "What is the maximum surge multiplier allowed at SFO?"
    print(f"\n--- Testing Policy Q&A Pipeline ---")
    print(f"Query: '{test_query}'\n")
    
    result = answer_policy_question(test_query)
    
    print("Answer:")
    print(result["answer"])
    print("\nSource(s):")
    for src in result["sources"]:
        print(f"- {src}")