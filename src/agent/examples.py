from src.prompts.template import apply_prompt_template, render_prompt_template
from langgraph.prebuilt import create_react_agent
from src.llmproxy.llm_api import OpenAIClient
from src.agent.tools import tavily_search, web_crawl
from src.agent.agents import AgentState
from langgraph_supervisor import create_supervisor
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.types import Command
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig
from typing import Literal
from loguru import logger
from langchain_core.messages import HumanMessage, AIMessage

client = OpenAIClient("ep-20250619111741-nx8jc")
llm = client.get_llm()
agent_state = AgentState(locale="zh-CN")

researcher = create_react_agent(
    llm,
    tools=[tavily_search, web_crawl],
    prompt=render_prompt_template("researcher", agent_state),
    name="researcher",
)

planner = create_react_agent(
    llm,
    tools=[tavily_search],
    prompt=render_prompt_template("planner", agent_state),
    name="planner",
)

@tool
def handoff_to_planner(
    research_topic: Annotated[str, "The topic of the research task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to planner agent to do plan."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    return

# coordinator = create_react_agent(
#     llm,
#     tools=[handoff_to_planner],
#     prompt=render_prompt_template("coordinator", agent_state),
#     name="coordinator",
# )
def coordinator_node(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["planner", "__end__"]]:
    logger.info("Coordinator talking.")
    messages = apply_prompt_template("coordinator", state)
    response = llm.bind_tools([handoff_to_planner]).invoke(messages)
    logger.info(f'response={response}')
    locale = state.get("locale", "en-US")
    research_topic = state.get("research_topic", "")
    if len(response.tool_calls) > 0:
        goto = 'planner'
        for tool_call in response.tool_calls:
            if tool_call.get("name","") != 'handoff_to_planner':
                continue
            if tool_call.get("args", {}).get("locale") and tool_call.get("args", {}).get("research_topic"):
                locale = tool_call.get("args", {}).get("locale")
                research_topic = tool_call.get("args", {}).get("research_topic")
                break
        pass
    else:
        goto = "__end__"
        logger.warning(
            "Coordinator response contains no tool calls. Terminating workflow execution."
        )
    logger.warning(f'goto={goto}')
    return Command(
        update={"locale": locale, "research_topic": research_topic, "messages": [AIMessage(content=response.content)]},
        goto=goto,
    )


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
    .add_node("planner", planner)
    .add_node("researcher", researcher)
    .add_node("reporter", reporter)
    .add_edge("planner", "researcher")
    .add_edge("researcher", "planner")
    .add_edge("planner", "reporter")
    .add_edge("reporter", END)
    .compile()
)
