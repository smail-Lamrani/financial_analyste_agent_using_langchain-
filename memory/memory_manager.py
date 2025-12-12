from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """Simple conversation memory manager without vector embeddings"""
    
    def __init__(self, max_history: int = 10):
        self.memory = []
        self.max_history = max_history
    
    def add_interaction(self, user_input: str, agent_response: str, metadata: Dict = None):
        """Add interaction to memory"""
        try:
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "user": user_input,
                "assistant": agent_response,
                "metadata": metadata or {}
            }
            
            self.memory.append(interaction)
            
            # Keep only recent history
            if len(self.memory) > self.max_history:
                self.memory = self.memory[-self.max_history:]
                
        except Exception as e:
            logger.error(f"Memory add error: {e}")
    
    def get_conversation_history(self, limit: int = None) -> List[str]:
        """Get formatted conversation history"""
        try:
            history = []
            for item in self.memory[-(limit or self.max_history):]:
                history.append(f"User: {item['user']}")
                history.append(f"Assistant: {item['assistant']}")
            return history
        except Exception as e:
            logger.error(f"Memory get error: {e}")
            return []
    
    def get_context(self, current_query: str) -> str:
        """Get relevant context from memory"""
        try:
            # Simple keyword matching for relevance
            query_words = set(current_query.lower().split())
            relevant_interactions = []
            
            for item in self.memory[-5:]:  # Check last 5 interactions
                combined_text = f"{item['user']} {item['assistant']}".lower()
                # Count matching words
                matches = sum(1 for word in query_words if word in combined_text)
                if matches > 1:  # At least 2 matching words
                    relevant_interactions.append(item)
            
            # Format relevant context
            if relevant_interactions:
                context_lines = ["Previous relevant conversations:"]
                for item in relevant_interactions[-3:]:  # Last 3 relevant
                    context_lines.append(f"User: {item['user']}")
                    context_lines.append(f"Assistant: {item['assistant']}")
                return "\n".join(context_lines)
            return "No relevant previous conversations."
            
        except Exception as e:
            logger.error(f"Memory context error: {e}")
            return ""
    
    def clear(self):
        """Clear memory"""
        try:
            self.memory.clear()
        except Exception as e:
            logger.error(f"Memory clear error: {e}")