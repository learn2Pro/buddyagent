import operator
from typing import Annotated, List, Dict, Any, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool, tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import json
import requests
from datetime import datetime


# Define custom tools
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Mock weather API call
    weather_data = {
        "New York": "Sunny, 75°F",
        "London": "Cloudy, 60°F", 
        "Tokyo": "Rainy, 65°F",
        "Paris": "Partly cloudy, 68°F"
    }
    return weather_data.get(city, f"Weather data not available for {city}")


@tool
def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    try:
        # Only allow basic mathematical operations for safety
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Only basic mathematical operations are allowed"
        
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


@tool
def search_web(query: str) -> str:
    """Search the web for information (mock implementation)."""
    # Mock search results
    search_results = {
        "python": "Python is a high-level programming language known for its simplicity and versatility.",
        "ai": "Artificial Intelligence is the simulation of human intelligence in machines.",
        "langgraph": "LangGraph is a library for building stateful, multi-actor applications with LLMs.",
        "react": "ReAct (Reasoning and Acting) is a prompting technique that combines chain-of-thought reasoning with action execution."
    }
    
    for key, value in search_results.items():
        if key.lower() in query.lower():
            return f"Search results for '{query}': {value}"
    
    return f"No specific results found for '{query}'. This is a mock search implementation."


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_action: str


class ReactAgent:
    def __init__(self, llm):
        # Initialize the LLM
        self.llm = llm
        
        # Define available tools
        self.tools = [get_weather, calculate, search_web, get_current_time]
        self.tool_node = ToolNode(self.tools)
        
        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Create the graph
        self.graph = self._create_graph()
        
        # Add memory for conversation history
        self.memory = MemorySaver()
        self.app = self.graph.compile(checkpointer=self.memory)
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("agent", self._call_model)
        graph.add_node("tools", self.tool_node)
        
        # Add edges
        graph.set_entry_point("agent")
        graph.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        graph.add_edge("tools", "agent")
        
        return graph
    
    def _call_model(self, state: AgentState) -> Dict[str, Any]:
        """Call the LLM with the current state."""
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine whether to continue with tool calls or end."""
        last_message = state["messages"][-1]
        
        # If there are tool calls, continue to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        else:
            return "end"
    
    def run(self, user_input: str, thread_id: str = "default") -> str:
        """Run the agent with user input."""
        config = {"configurable": {"thread_id": thread_id}}
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=user_input)]
        }
        
        # Run the graph
        result = self.app.invoke(initial_state, config)
        
        # Return the last AI message
        return result["messages"][-1].content
    
    def stream(self, user_input: str, thread_id: str = "default"):
        """Stream the agent's responses."""
        config = {"configurable": {"thread_id": thread_id}}
        
        initial_state = {
            "messages": [HumanMessage(content=user_input)]
        }
        
        for output in self.app.stream(initial_state, config):
            for key, value in output.items():
                print(f"--- {key.upper()} ---")
                if "messages" in value:
                    for message in value["messages"]:
                        if hasattr(message, 'content') and message.content:
                            print(f"Content: {message.content}")
                        if hasattr(message, 'tool_calls') and message.tool_calls:
                            print(f"Tool calls: {message.tool_calls}")
                print()


# Example usage and demonstration
def main():
    """Demonstrate the React Agent with various examples."""
    print("🤖 Initializing React Agent with LangGraph...")
    
    from src.llmproxy.llm_api import OpenAIClient
    client = OpenAIClient('gpt-4o')
    # Create the agent
    agent = ReactAgent(client.get_llm())
    
    print("✅ Agent initialized successfully!\n")
    
    # Example interactions
    examples = [
        "What's the weather like in New York?",
        "Calculate 25 * 4 + 10",
        "What is LangGraph? Search for information about it.",
        "What time is it right now?",
        "What's the weather in London and what's 15 + 27?",
    ]
    
    print("🚀 Running example interactions:\n")
    
    for i, example in enumerate(examples, 1):
        print(f"Example {i}: {example}")
        print("-" * 50)
        
        try:
            response = agent.run(example, thread_id=f"example_{i}")
            print(f"Agent: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")
    
    print("💡 You can also use agent.stream() for real-time streaming responses!")
    
    # Interactive mode
    print("\n🎯 Interactive Mode (type 'quit' to exit):")
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        try:
            response = agent.run(user_input, thread_id="interactive")
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()


# # Additional utility functions for advanced usage
# class ReactAgentBuilder:
#     """Builder class for creating customized React agents."""
    
#     def __init__(self):
#         self.tools = []
#         self.model_name = "gpt-3.5-turbo"
#         self.system_prompt = None
    
#     def add_tool(self, tool: BaseTool):
#         """Add a custom tool to the agent."""
#         self.tools.append(tool)
#         return self
    
#     def set_model(self, model_name: str):
#         """Set the LLM model to use."""
#         self.model_name = model_name
#         return self
    
#     def set_system_prompt(self, prompt: str):
#         """Set a custom system prompt."""
#         self.system_prompt = prompt
#         return self
    
#     def build(self) -> ReactAgent:
#         """Build the configured React agent."""
#         agent = ReactAgent(self.model_name)
        
#         if self.tools:
#             agent.tools.extend(self.tools)
#             agent.tool_node = ToolNode(agent.tools)
#             agent.llm_with_tools = agent.llm.bind_tools(agent.tools)
        
#         return agent


# # Example of creating a custom tool
# @tool
# def generate_password(length: int = 12) -> str:
#     """Generate a secure random password of specified length."""
#     import random
#     import string
    
#     if length < 4:
#         length = 4
#     elif length > 50:
#         length = 50
    
#     characters = string.ascii_letters + string.digits + "!@#$%^&*"
#     password = ''.join(random.choice(characters) for _ in range(length))
#     return f"Generated password: {password}"


# # Example of using the builder pattern
# def create_custom_agent():
#     """Example of creating a custom agent with additional tools."""
#     builder = ReactAgentBuilder()
#     custom_agent = (builder
#                    .add_tool(generate_password)
#                    .set_model("gpt-4")
#                    .build())
    
#     return custom_agent