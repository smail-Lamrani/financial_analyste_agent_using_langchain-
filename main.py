"""
Financial Assistant - Interactive CLI Application

This is the main entry point for the Financial Assistant application.
Provides an interactive command-line interface for stock analysis.

Usage:
    # Interactive mode
    python main.py
    
    # Single query mode (not yet implemented)
    python main.py "What is NVIDIA stock price?"

Features:
    - Real-time stock data via yfinance
    - News search via DuckDuckGo
    - Multi-language support (English/French)
    - Cache support (Redis + in-memory)
    - Query performance tracking

Example Session:
    $ python main.py
    🤖 Financial Assistant (Tool-First Architecture)
    💬 You: What is the current stock price of NVIDIA?
    
    📊 Stock Data for NVDA
    - Current Price: $180.93 USD
    - Volume: 181,596,600
    ...
"""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from agents.orchestrator import MultiAgentOrchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class FinancialAssistant:
    """
    Main financial assistant application with interactive CLI.
    
    This class manages the user interaction loop and delegates
    queries to the MultiAgentOrchestrator.
    
    Attributes:
        orchestrator (MultiAgentOrchestrator): Handles query routing
        query_count (int): Number of queries processed this session
    
    Example:
        >>> assistant = FinancialAssistant()
        >>> await assistant.chat()  # Start interactive session
    """
    
    def __init__(self):
        """Initialize the assistant with orchestrator."""
        self.orchestrator = MultiAgentOrchestrator()
        self.query_count = 0
    
    async def ask(self, question: str) -> Dict[str, Any]:
        """
        Process a single question and return response with metadata.
        
        Args:
            question: User's natural language query
        
        Returns:
            Dict containing:
                - success (bool): True if query succeeded
                - response (str): The assistant's response
                - response_time (float): Query processing time in seconds
                - error (str, optional): Error message if failed
        
        Example:
            >>> result = await assistant.ask("NVIDIA stock price")
            >>> print(result['response'])
            >>> print(f"Took {result['response_time']:.2f}s")
        """
        self.query_count += 1
        
        try:
            print(f"\n📊 Processing query {self.query_count}: {question}")
            print("-" * 60)
            
            start_time = datetime.now()
            response = await self.orchestrator.query(question)
            response_time = (datetime.now() - start_time).total_seconds()
            
            print(f"\n✅ Response (took {response_time:.2f}s):")
            print("-" * 60)
            print(response)
            
            return {
                "success": True,
                "response": response,
                "response_time": response_time
            }
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": f"Sorry, I encountered an error: {str(e)}"
            }
    
    def chat(self):
        """Interactive chat mode"""
        print("\n🤖 Financial Assistant")
        print("=" * 60)
        print("Type 'quit' to exit, 'clear' to clear memory")
        
        while True:
            try:
                question = input("\n💬 You: ").strip()
                
                if question.lower() == 'quit':
                    print("Goodbye!")
                    break
                
                if question.lower() == 'clear':
                    self.orchestrator.clear_memory()
                    print("Memory cleared!")
                    continue
                
                if not question:
                    continue
                
                # Run async query
                response = asyncio.run(self.ask(question))
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nUnexpected error: {e}")

# Example usage
if __name__ == "__main__":
    import sys
    
    # Check for API key
    from config.settings import settings
    if not settings.HUGGINGFACEHUB_API_TOKEN:
        print("❌ Error: HUGGINGFACEHUB_API_TOKEN not found in .env file")
        print("Please create a .env file with: HUGGINGFACEHUB_API_TOKEN=your_token_here")
        sys.exit(1)
    
    # Create assistant
    assistant = FinancialAssistant()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Run single query from command line
        question = " ".join(sys.argv[1:])
        asyncio.run(assistant.ask(question))
    else:
        # Start interactive chat
        assistant.chat()
