from typing import List, Dict, Any, Optional


class ConversationMemory:
    """
    Tracks conversation history and active context state across turns.
    """
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.history: List[Dict[str, str]] = []
        self.active_airport: Optional[str] = None

    def add_message(self, role: str, content: str):
        """Appends a message to the history and trims to max_turns."""
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-(self.max_turns * 2):]

    def update_active_airport(self, airport_code: str):
        """Tracks the currently referenced airport (e.g., SFO, LAX, JFK)."""
        if airport_code and airport_code.upper() in ["SFO", "LAX", "JFK"]:
            self.active_airport = airport_code.upper()

    def get_context_summary(self) -> str:
        """Formats conversation history for LLM prompt context."""
        if not self.history:
            return "No previous conversation history."
        
        summary = []
        if self.active_airport:
            summary.append(f"Active Focused Airport: {self.active_airport}")
        
        summary.append("Recent Conversation History:")
        for msg in self.history:
            summary.append(f"{msg['role'].capitalize()}: {msg['content']}")
            
        return "\n".join(summary)

    def clear(self):
        """Clears memory."""
        self.history = []
        self.active_airport = None

if __name__ == "__main__":
    mem = ConversationMemory()
    mem.add_message("user", "Check SFO metrics.")
    mem.update_active_airport("SFO")
    mem.add_message("assistant", "SFO completion rate is 71%.")
    
    print("--- Memory Context Preview ---")
    print(mem.get_context_summary())