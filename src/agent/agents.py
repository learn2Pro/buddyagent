from abc import abstractmethod
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain.agents import Tool
from langchain_tavily import TavilySearch
from tools import tavily_search, arxiv_search


class BaseAgent:
    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    def invoke(self, input: str):
        pass


class SearchAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.agent_type = "searcher"

    def invoke(self, messages):
        from langchain import hub
        from langchain.agents import AgentExecutor, create_react_agent
        from langchain.prompts import PromptTemplate
        from langgraph.checkpoint.memory import MemorySaver
        # from langgraph.prebuilt import create_react_agent


        prompt = hub.pull("hwchase17/react")
        agent = create_react_agent(
            llm=self.llm,
            tools=[tavily_search],
            prompt=prompt,
        )
        agent_executor = AgentExecutor(
            agent=agent,
            tools=[tavily_search],
            handle_parsing_errors=True,
        )
        return agent_executor.stream(input=messages)

        # memory = MemorySaver()
        # self.llm.bind_tools([tavily_search])
        # agent = create_react_agent(
        #     model=self.llm,
        #     tools=[tavily_search],
        #     checkpointer=memory,
        #     prompt="You are a helpful assistant",
        #     # prompt=prompt,
        # )
        # config = {"configurable": {'thread_id': '123'}}

        # return agent.stream({'messages': messages}, config, stream_mode="values",)



if __name__ == "__main__":

    from src.llmproxy.llm_api import OpenAIClient

    client = OpenAIClient("gpt-4o-mini")
    # Step 1: 初始化 LLM
    agent = SearchAgent(client.get_llm())
    # Step 5: 执行 agent 搜索问题
    from langchain_core.messages import AIMessage, HumanMessage
    # response = agent.invoke([{"role": "user", "content": "Who won the NBA championship in 2025?"}])
    # response = agent.invoke([HumanMessage('whats the weather where I live?')])
    response = agent.invoke({"input": "Who won the NBA championship in 2025?"})
    for step in response:
        step["messages"][-1].pretty_print()
    # Step 6: 打印结果
    # print(response)
