from langchain.tools.base import BaseTool
from typing import List
from langgraph.graph import StateGraph, START, END, MessagesState

class AgentState(MessagesState):
    """State for the agent system, extends MessagesState with next field."""
    research_topic:str
    next_action: str
    locale: str
