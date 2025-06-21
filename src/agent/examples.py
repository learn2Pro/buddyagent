from src.prompts.template import apply_prompt_template, render_prompt_template
from langgraph.prebuilt import create_react_agent
from src.llmproxy.llm_api import OpenAIClient
from src.agent.tools import tavily_search, web_crawl
from src.agent.agents import AgentState
from langgraph.graph import START, END, StateGraph, MessagesState
from loguru import logger
from src.agent.agents import coordinator_node, planner_node, human_feedback_node, research_team_node, researcher_node

client = OpenAIClient("ep-20250619111741-nx8jc")
llm = client.get_llm()
agent_state = AgentState(locale="zh-CN")

researcher = create_react_agent(
    llm,
    tools=[tavily_search, web_crawl],
    prompt=render_prompt_template("researcher", agent_state),
    name="researcher",
)

# coordinator = create_react_agent(
#     llm,
#     tools=[handoff_to_planner],
#     prompt=render_prompt_template("coordinator", agent_state),
#     name="coordinator",
# )


reporter = create_react_agent(
    llm,
    tools=[],
    prompt=render_prompt_template("reporter", agent_state),
    name="reporter",
)


supervisor = (
    StateGraph(AgentState)
    .add_edge(START, "coordinator")
    .add_node("coordinator", coordinator_node)
    .add_node("planner", planner_node)
    .add_node("human_feedback", human_feedback_node)
    .add_node("research_team", research_team_node)
    .add_node("researcher", researcher_node)
    .add_node("reporter", reporter)
    .add_edge("reporter", END)
    .compile()
)
