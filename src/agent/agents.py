from abc import abstractmethod
from langchain_openai import ChatOpenAI
from src.agent.tools import web_search, arxiv_search, web_crawl, handoff_to_planner
from src.agent.state import AgentState
from src.prompts.template import (
    render_prompt_template,
    apply_prompt_template,
)
import uuid
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from loguru import logger
from src.llmproxy.llm_api import UnifiedLLMClient
from langgraph.types import Command, interrupt
from typing import Literal
from src.agent.state import Plan, StepType
from src.conf.config_loader import config_data

activate_llm = config_data["llm"]["activate"]
client = UnifiedLLMClient(activate_llm)
llm = client.get_llm()


def coordinator_node(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["planner", "__end__"]]:
    """the coordinator node reply to user and handoff to planner"""
    logger.info("Coordinator talking.")
    messages = apply_prompt_template("coordinator", state)
    response = llm.bind_tools([handoff_to_planner]).invoke(messages)
    # logger.info(f"Coordinator messages={messages} response={response}")
    locale = state.get("locale", "zh-CN")
    research_topic = state.get("research_topic", "")
    content = response.content
    if len(response.tool_calls) > 0:
        goto = "planner"
        for tool_call in response.tool_calls:
            if tool_call.get("name", "") != "handoff_to_planner":
                continue
            if tool_call.get("args", {}).get("locale") and tool_call.get(
                "args", {}
            ).get("research_topic"):
                locale = tool_call.get("args", {}).get("locale")
                research_topic = tool_call.get("args", {}).get("research_topic")
                content = f"Transfer to planner to analyze the research topic: {research_topic}!!!"
                break
    elif 'handoff_to_planner' in response.content:
        goto = "planner"
        research_topic = state.get("messages", [])[-1].content
        content = f"Transfer to planner to analyze the research topic: {research_topic}!!!"
    else:
        goto = "__end__"
        logger.warning(f"Coordinator response contains no tool calls={response.content}. \n>>>>Terminating workflow execution.")
    return Command(
        update={
            "locale": locale,
            "research_topic": research_topic,
            "messages": [AIMessage(content=content)],
        },
        goto=goto,
    )


def planner_node(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["human_feedback", "reporter", "__end__"]]:
    """the planner node receive user request and generate full plan"""

    logger.info("Planner Thinking...")
    plan_iteration = state.get("plan_iteration", 0)
    messages = apply_prompt_template("planner", state)
    logger.warning(f"plan_iteration={plan_iteration} messages={messages}")
    response = llm.invoke(messages)
    full_plan = response.content

    try:
        # json_plan = json.loads(full_plan_json)
        plan = Plan.model_validate_json(full_plan)
        # full_plan = format_plan(plan)
    except:
        logger.warning(
            f"Planner response is not a valid JSON string. response={full_plan}"
        )
        if plan_iteration > 0:
            return Command(
                update={
                    "messages": [AIMessage(content=full_plan)],
                },
                goto="reporter",
            )
        else:
            return Command(
                update={
                    "messages": [AIMessage(content=full_plan)],
                },
                goto="__end__",
            )

    if plan.has_enough_context:
        return Command(
            update={
                "curr_plan": plan,
                "messages": [AIMessage(content=full_plan)],
            },
            goto="reporter",
        )

    return Command(
        update={
            "curr_plan": plan,
            "messages": [AIMessage(content=full_plan)],
        },
        goto="human_feedback",
    )


def human_feedback_node(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["planner", "research_team", "reporter"]]:
    """the human feedback node reply to user and handoff to planner or reporter"""
    logger.info("Receiving Human Feedback...")
    # feedback = interrupt("Please Review the plan...")
    # logger.warning(f"human feedback={feedback}")
    plan_iteration = state.get("plan_iteration", 0) + 1
    goto = "research_team"
    if state["curr_plan"] and state["curr_plan"].has_enough_context:
        goto = "reporter"
    return Command(
        update={
            "plan_iteration": plan_iteration,
        },
        goto=goto,
    )


def research_team_node(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["planner", "researcher"]]:
    """the research team node receive user request and generate full plan"""

    def continue_to_running_research_team():
        current_plan = state.get("curr_plan")
        if not current_plan or not current_plan.steps:
            return "planner"
        if all(step.execution_res for step in current_plan.steps):
            return "planner"
        for step in current_plan.steps:
            if not step.execution_res:
                break
        if step.step_type and step.step_type == StepType.RESEARCH:
            return "researcher"
        if step.step_type and step.step_type == StepType.PROCESSING:
            return "coder"
        return "planner"

    goto = continue_to_running_research_team()
    return Command(goto=goto)


def get_complete_and_curr_step(state: AgentState):
    completed_steps = []
    curr_plan = state["curr_plan"]
    for curr_step in curr_plan.steps:
        if curr_step.execution_res is None:
            break
        completed_steps.append(curr_step)
    return completed_steps, curr_step


def researcher_node(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """the researcher node receive user request and generate full plan"""
    logger.info("Researcher Thinking...")
    researcher = create_react_agent(
        llm,
        tools=[web_search, web_crawl],
        prompt=render_prompt_template("researcher", state),
        name="researcher",
    )
    completed_steps, curr_step = get_complete_and_curr_step(state)
    observations = state.get("observations", [])
    # Format completed steps information
    completed_steps_info = ""
    if completed_steps:
        completed_steps_info = "# Existing Research Findings\n\n"
        for i, step in enumerate(completed_steps):
            completed_steps_info += f"## Existing Finding {i + 1}: {step.title}\n\n"
            completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"

    current_task_info = f"# Current Task\n\n## Title\n\n{curr_step.title}\n\n## Description\n\n{curr_step.description}\n\n## Locale\n\n{state.get('locale', 'en-US')}"
    messages = {
        "messages": [
            HumanMessage(content=f"{completed_steps_info}{current_task_info}"),
            # append notice
            HumanMessage(
                content="IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
                name="system",
            ),
        ]
    }
    response = researcher.invoke(input=messages)
    logger.info(f"research return={response}")
    content = response["messages"][-1].content
    curr_step.execution_res = content

    return Command(
        update={
            "messages": [AIMessage(content=content)],
            "observations": observations + [content],
        },
        goto="research_team",
    )


def reporter_node(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["planner", "__end__"]]:
    """the reporter node reply to user and handoff to planner or reporter"""
    curr_plan = state.get("curr_plan", None)
    logger.info(f"Reporter Thinking current_plan={curr_plan}...")
    messages = apply_prompt_template("reporter", state)
    response = llm.invoke(messages)
    content = response.content
    return Command(
        update={
            "messages": [AIMessage(content=content)],
        },
        goto="__end__",
    )


# class BaseAgent:
#     def __init__(self, llm: ChatOpenAI):
#         self.llm = llm

#     @abstractmethod
#     def invoke(self, input: str):
#         pass


# class SearchAgent(BaseAgent):
#     def __init__(self, llm: ChatOpenAI):
#         super().__init__(llm)
#         self.agent_type = "researcher"
#         self.researcher = create_react_agent(
#             self.llm,
#             tools=[tavily_search, web_crawl],
#             name=self.agent_type,
#             prompt=render_prompt_template(self.agent_type, AgentState()),
#         )

#     def get_agent(self):
#         return self.researcher

#     def stream(self, messages: str):
#         # from langchain import hub
#         # from langchain.agents import AgentExecutor, create_react_agent
#         # from langgraph.checkpoint.memory import MemorySaver

#         # # prompt = hub.pull("hwchase17/react")
#         # # prompt = ReactPromptTemplate()
#         # prompt = PromptTemplate(
#         #     input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
#         #     template=render_prompt_template("react", AgentState()),
#         # )
#         # tools = [tavily_search, arxiv_search]
#         # agent = create_react_agent(
#         #     llm=self.llm,
#         #     tools=tools,
#         #     prompt=prompt,
#         # )
#         # agent_executor = AgentExecutor(
#         #     agent=agent,
#         #     tools=tools,
#         #     handle_parsing_errors=True,
#         # )
#         # return agent_executor.stream(input=messages)

#         return self.researcher.stream(
#             input={"messages": messages},
#             stream_mode="values",
#             config={"thread_id": uuid.uuid4()},
#         )


if __name__ == "__main__":
    coordinator_node(AgentState(), {"thread_id": uuid.uuid4()})
