from abc import abstractmethod
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain.agents import Tool
from langchain_tavily import TavilySearch
from src.agent.tools import tavily_search, arxiv_search, web_crawl
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.agent.state import AgentState
from src.prompts.template import (
    render_base_prompt_tpl,
    render_prompt_template,
    apply_prompt_template,
)
import uuid
from langgraph.prebuilt import create_react_agent


class BaseAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    @abstractmethod
    def invoke(self, input: str):
        pass


class SearchAgent(BaseAgent):
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.agent_type = "researcher"
        self.researcher = create_react_agent(
            self.llm,
            tools=[tavily_search, web_crawl],
            name=self.agent_type,
            prompt=render_prompt_template(self.agent_type, AgentState()),
        )

    def get_agent(self):
        return self.researcher

    def stream(self, messages: str):
        # from langchain import hub
        # from langchain.agents import AgentExecutor, create_react_agent
        # from langgraph.checkpoint.memory import MemorySaver

        # # prompt = hub.pull("hwchase17/react")
        # # prompt = ReactPromptTemplate()
        # prompt = PromptTemplate(
        #     input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
        #     template=render_prompt_template("react", AgentState()),
        # )
        # tools = [tavily_search, arxiv_search]
        # agent = create_react_agent(
        #     llm=self.llm,
        #     tools=tools,
        #     prompt=prompt,
        # )
        # agent_executor = AgentExecutor(
        #     agent=agent,
        #     tools=tools,
        #     handle_parsing_errors=True,
        # )
        # return agent_executor.stream(input=messages)

        return self.researcher.stream(
            input={"messages": messages},
            stream_mode="values",
            config={"thread_id": uuid.uuid4()},
        )


if __name__ == "__main__":

    from src.llmproxy.llm_api import OpenAIClient

    client = OpenAIClient("ep-20250619111741-nx8jc")
    # Step 1: 初始化 LLM
    agent = SearchAgent(client.get_llm())
    # Step 5: 执行 agent 搜索问题
    from langchain_core.messages import AIMessage, HumanMessage
    from langgraph.graph.graph import CompiledGraph

    response = agent.stream(
        [{"role": "user", "content": "Who won the NBA championship in 2025?"}]
    )
    # response = agent.invoke([HumanMessage('Who won the NBA championship in 2025?')])
    # response = agent.invoke({"input": "Who won the NBA championship in 2025?"})
    for step in response:
        # print(step.content)
        step["messages"][-1].pretty_print()
