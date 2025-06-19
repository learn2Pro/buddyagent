from langgraph.graph import StateGraph, START, END, MessagesState
from src.agent.agents import SearchAgent
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from src.agent.state import AgentState

def build_graph(llm):
    graph = StateGraph(AgentState)
    graph.add_node(START)
    graph.add_node("researcher", SearchAgent(llm))
    graph.add_node(END)
    graph.add_edge(START, "researcher", "END")
    return graph.compile()

if __name__ == "__main__":
    from src.llmproxy.llm_api import OpenAIClient
    client = OpenAIClient('gpt-4o-mini')
    graph = build_graph(client.get_llm())
    print(graph)
    # Step 5: 调用执行
    output = graph.invoke({"input": "牛顿出生在哪一年？再加上 100"})
    print("\n🧠 Agent 回答:\n", output["result"])