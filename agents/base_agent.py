from typing import List, Dict, Any, Optional
import asyncio
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from memory.memory_manager import MemoryManager
from cache.cache_manager import cache_manager
from config.settings import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base agent with memory and caching"""
    
    def __init__(
        self,
        name: str,
        role: str,
        tools: List[BaseTool],
        model_name: Optional[str] = None,
        use_cache: bool = True
    ):
        self.name = name
        self.role = role
        self.tools = tools
        self.use_cache = use_cache
        
        # Initialize LLM
        llm_endpoint = HuggingFaceEndpoint(
            repo_id=model_name or settings.PRIMARY_MODEL,
            task="text-generation",
            max_new_tokens=512,
            do_sample=False,
            temperature=0.0,
            repetition_penalty=1.1,
            stop_sequences=["\nObservation:", "Observation:"],
            huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN
        )
        self.llm = ChatHuggingFace(llm=llm_endpoint)
        
        # Initialize memory
        self.memory = MemoryManager()
        
        # Create agent
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create LangChain agent"""
        
        # Define prompt template - Standard ReAct format
        prompt = PromptTemplate.from_template(
            """Answer the following questions as best you can. You are {name}, {role}

Current date: {current_date}

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT: 
- Only use the tools listed above
- Do NOT invent tool names
- Wait for the Observation before continuing
- Give a concise Final Answer

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
        )
        
        # Create ReAct agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,#avant était 5 
            # early_stopping_method="generate"  # Unsupported in current version
        )
        
        return executor
    
    async def query(self, query: str) -> str:
        """Execute agent query with caching"""
        
        # Generate cache key
        cache_key = cache_manager._generate_key(f"agent_{self.name}", query)
        
        # Check cache
        if self.use_cache:
            cached_response = cache_manager.get(cache_key)
            if cached_response:
                logger.info(f"Using cached response for {self.name}")
                return cached_response
        
        try:
            # Get conversation context
            context = self.memory.get_context(query)
            
            # Prepare input
            input_data = {
                "name": self.name,
                "role": self.role,
                "current_date": datetime.now().strftime("%Y-%m-%d"),
                "input": query,
                "tool_names": ", ".join([tool.name for tool in self.tools])
            }
            
            # Execute agent (using sync invoke to avoid AsyncInferenceClient issues)
            result = await asyncio.to_thread(self.agent.invoke, input_data)
            response = result["output"]
            
            # Cache response
            if self.use_cache:
                cache_manager.set(cache_key, response, ttl=settings.CACHE_TTL)
            
            # Add to memory
            self.memory.add_interaction(query, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Agent {self.name} error: {e}")
            return f"I encountered an error: {str(e)}. Please try again."