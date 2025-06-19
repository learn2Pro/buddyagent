from src.prompts.template import apply_prompt_template, render_prompt_template
from langgraph.prebuilt import create_react_agent
from src.llmproxy.llm_api import OpenAIClient
from src.agent.tools import tavily_search, web_crawl
from src.agent.agents import AgentState
from langgraph_supervisor import create_supervisor

client = OpenAIClient('ep-20250619111741-nx8jc')
llm = client.get_llm()

researcher = create_react_agent(
    llm,
    tools=[tavily_search, web_crawl],
    prompt=render_prompt_template("researcher", AgentState()),
    name="researcher",
)

planner = create_react_agent(
    llm,
    tools=[tavily_search],
    prompt=render_prompt_template("planner", AgentState()),
    name="planner",
)

supervisor = create_supervisor(
    [planner, researcher],
    model=llm,
    prompt=render_prompt_template("supervisor", AgentState()),
).compile()
