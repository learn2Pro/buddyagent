from langchain.tools.base import BaseTool
from typing import List, Optional
from enum import Enum
from langgraph.graph import StateGraph, START, END, MessagesState
from pydantic import Field, BaseModel


class StepType(str, Enum):
    RESEARCH = "research"
    PROCESSING = "processing"



class Step(BaseModel):
    need_search: bool = Field(..., description="Must be explicitly set for each step")
    title: str
    description: str = Field(..., description="Specify exactly what data to collect")
    step_type: StepType = Field(..., description="Indicates the nature of the step")
    execution_res: Optional[str] = Field(
        default=None, description="The Step execution result"
    )


class Plan(BaseModel):
    locale: str = Field(
        ..., description="e.g. 'en-US' or 'zh-CN', based on the user's language"
    )
    has_enough_context: bool
    thought: str
    title: str
    steps: List[Step] = Field(
        default_factory=list,
        description="Research & Processing steps to get more context",
    )

class AgentState(MessagesState):
    """State for the agent system, extends MessagesState with next field."""

    research_topic: str
    next_action: str
    locale: str
    max_step_num: int = 3
    plan_iteration: int = 0
    curr_plan: Optional[Plan] = Field(
        default=None, description="The current plan for the agent"
    )
    observations:List[str] = []



if __name__ == "__main__":
    plan = Plan.model_validate_json(
        """{"locale": "zh-CN", "has_enough_context": false, "thought": "\u7528\u6237\u5e0c\u671b\u5206\u6790Labubu\u706b\u7206\u7684\u539f\u56e0\uff0c\u76ee\u524d\u6ca1\u6709\u8db3\u591f\u7684\u4fe1\u606f\u6765\u5168\u9762\u56de\u7b54\u8be5\u95ee\u9898\uff0c\u9700\u8981\u4ece\u5386\u53f2\u80cc\u666f\u3001\u5f53\u524d\u5e02\u573a\u60c5\u51b5\u3001\u6d88\u8d39\u8005\u7b49\u5229\u76ca\u76f8\u5173\u8005\u3001\u5b9a\u91cf\u548c\u5b9a\u6027\u6570\u636e\u7b49\u591a\u4e2a\u65b9\u9762\u8fdb\u884c\u4fe1\u606f\u6536\u96c6\u3002", "title": "\u5206\u6790Labubu\u706b\u7684\u539f\u56e0", "steps": [{"need_search": true, "title": "Labubu\u7684\u5386\u53f2\u53d1\u5c55\u4e0e\u6f14\u53d8", "description": "\u67e5\u627eLabubu\u7684\u8bde\u751f\u65f6\u95f4\u3001\u8bbe\u8ba1\u5e08\u80cc\u666f\u3001\u6700\u521d\u7684\u8bbe\u8ba1\u7406\u5ff5\u548c\u5f62\u8c61\u7279\u70b9\uff1b\u68b3\u7406Labubu\u4ece\u8bde\u751f\u5230\u706b\u7206\u7684\u53d1\u5c55\u5386\u7a0b\uff0c\u5305\u62ec\u91cd\u8981\u7684\u65f6\u95f4\u8282\u70b9\u548c\u5173\u952e\u4e8b\u4ef6\uff1b\u5206\u6790Labubu\u5728\u4e0d\u540c\u9636\u6bb5\u7684\u5f62\u8c61\u548c\u98ce\u683c\u53d8\u5316\uff0c\u4ee5\u53ca\u8fd9\u4e9b\u53d8\u5316\u80cc\u540e\u7684\u539f\u56e0\u3002", "step_type": "research"}, {"need_search": true, "title": "Labubu\u7684\u5f53\u524d\u5e02\u573a\u72b6\u51b5", "description": "\u6536\u96c6Labubu\u5f53\u524d\u7684\u5e02\u573a\u9500\u552e\u6570\u636e\uff0c\u5982\u9500\u552e\u989d\u3001\u9500\u552e\u91cf\u3001\u9500\u552e\u6e20\u9053\u7b49\uff1b\u5206\u6790Labubu\u5728\u4e0d\u540c\u5730\u533a\u3001\u4e0d\u540c\u6d88\u8d39\u7fa4\u4f53\u4e2d\u7684\u53d7\u6b22\u8fce\u7a0b\u5ea6\uff1b\u7814\u7a76Labubu\u5f53\u524d\u7684\u4ea7\u54c1\u7ebf\u548c\u7cfb\u5217\uff0c\u4ee5\u53ca\u5404\u7cfb\u5217\u7684\u7279\u70b9\u548c\u5e02\u573a\u53cd\u9988\u3002", "step_type": "research"}, {"need_search": true, "title": "Labubu\u7684\u672a\u6765\u5e02\u573a\u9884\u6d4b", "description": "\u67e5\u627e\u5e02\u573a\u7814\u7a76\u673a\u6784\u6216\u4e13\u5bb6\u5bf9Labubu\u672a\u6765\u5e02\u573a\u53d1\u5c55\u7684\u9884\u6d4b\u548c\u5206\u6790\uff1b\u5206\u6790\u5f71\u54cdLabubu\u672a\u6765\u53d1\u5c55\u7684\u56e0\u7d20\uff0c\u5982\u5e02\u573a\u8d8b\u52bf\u3001\u7ade\u4e89\u6001\u52bf\u3001\u6d88\u8d39\u8005\u9700\u6c42\u53d8\u5316\u7b49\uff1b\u63a2\u8ba8Labubu\u53ef\u80fd\u9762\u4e34\u7684\u6311\u6218\u548c\u673a\u9047\u3002", "step_type": "research"}, {"need_search": true, "title": "Labubu\u76f8\u5173\u5229\u76ca\u76f8\u5173\u8005\u5206\u6790", "description": "\u7814\u7a76Labubu\u7684\u54c1\u724c\u65b9\u3001\u8bbe\u8ba1\u5e08\u3001\u7ecf\u9500\u5546\u3001\u6d88\u8d39\u8005\u7b49\u5229\u76ca\u76f8\u5173\u8005\u7684\u89d2\u8272\u548c\u4f5c\u7528\uff1b\u5206\u6790\u4e0d\u540c\u5229\u76ca\u76f8\u5173\u8005\u5bf9Labubu\u7684\u671f\u671b\u548c\u9700\u6c42\uff1b\u6536\u96c6\u4e0d\u540c\u5229\u76ca\u76f8\u5173\u8005\u5bf9Labubu\u7684\u8bc4\u4ef7\u548c\u53cd\u9988\u3002", "step_type": "research"}, {"need_search": true, "title": "Labubu\u706b\u7206\u539f\u56e0\u7684\u5b9a\u6027\u4e0e\u5b9a\u91cf\u5206\u6790\u6570\u636e\u6536\u96c6", "description": "\u6536\u96c6\u5173\u4e8eLabubu\u706b\u7206\u539f\u56e0\u7684\u5b9a\u6027\u5206\u6790\uff0c\u5982\u6d88\u8d39\u8005\u7684\u8bc4\u4ef7\u3001\u5a92\u4f53\u7684\u62a5\u9053\u3001\u4e13\u5bb6\u7684\u89c2\u70b9\u7b49\uff1b\u67e5\u627e\u4e0eLabubu\u706b\u7206\u76f8\u5173\u7684\u5b9a\u91cf\u6570\u636e\uff0c\u5982\u793e\u4ea4\u5a92\u4f53\u7684\u5173\u6ce8\u5ea6\u3001\u8bdd\u9898\u70ed\u5ea6\u3001\u7c89\u4e1d\u589e\u957f\u6570\u91cf\u7b49\u3002", "step_type": "research"}]}"""
    )
    print(plan)
