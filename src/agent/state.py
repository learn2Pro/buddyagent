from langchain.tools.base import BaseTool
from typing import List
from langgraph.graph import StateGraph, START, END, MessagesState

class AgentState(MessagesState):
    """State for the agent system, extends MessagesState with next field."""
    next_action: str
    tools: List[BaseTool]
    tool_names: List[str]