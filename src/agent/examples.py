from src.prompts.template import apply_prompt_template, render_prompt_template
from langgraph.prebuilt import create_react_agent
from src.llmproxy.llm_api import OpenAIClient
from src.agent.tools import web_search, web_crawl
from src.agent.agents import AgentState
from langgraph.graph import START, END, StateGraph, MessagesState
from loguru import logger
from src.agent.agents import coordinator_node, planner_node, human_feedback_node, research_team_node, researcher_node, reporter_node


supervisor = (
    StateGraph(AgentState)
    .add_edge(START, "coordinator")
    .add_node("coordinator", coordinator_node)
    .add_node("planner", planner_node)
    .add_node("human_feedback", human_feedback_node)
    .add_node("research_team", research_team_node)
    .add_node("researcher", researcher_node)
    .add_node("reporter", reporter_node)
    .compile()
)
