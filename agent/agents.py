from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langgraph.prebuilt import create_react_agent


class Agent:
    def __init__(self, llm):
        self.llm = llm

    def chat_completion(self, messages):
        pass


def SearchAgent(Agent):
    def __init__(self, llm):
        super().__init__(llm)
        # 创建一个 Tavily Search 工具
        # Tavily 是知名的搜索引擎 API 提供商
        self.web_search = TavilySearchResults(
            name="web_search"     # 将该工具重新命名为“web_search”
        )

        # 创建一个 ReAct 风格的联网搜索 agent
        self.researcher_agent = create_react_agent(
            name="DeepLink",    # 取一个好听的名字
            model=self.llm,        # 指定模型，LangChain 支持市面上几乎所有的大语言模型
            tools=[self.web_search], # 为 Agent 分配一个或多个的工具
            prompt=my_prompt    # Prompt 请参考下一章节
        )


    def chat_completion(self, messages):
        pass


if __name__ == "__main__":
    
    llm = OpenAI(model_name="gpt-4o", api_base="http://127.0.0.1:8000/v1", api_key="xxx", temperature=0.1, max_tokens=2048)
    agent = SearchAgent(llm)
    agent.chat_completion(messages=[{"role": "user", "content": "Hello, world!"}])
