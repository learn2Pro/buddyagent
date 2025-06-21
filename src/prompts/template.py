from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.agent.state import AgentState
from datetime import datetime
import os
from src.agent.tools import tavily_search, arxiv_search
from langchain_core.prompts import BasePromptTemplate

env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


# class ReactPromptTemplate(BasePromptTemplate):
#     def __init__(self, **kwargs):
#         super().__init__(input_variables=["input", "tools", "tool_names", "agent_scratchpad"])
#         # self.prompt_name = "react"

#     def format_prompt(self, **kwargs):
#         # implement your formatting logic
#         print(f"kwargs: {kwargs}")
#         state_vars = {
#             "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
#             **kwargs,
#         }
#         template = env.get_template(f"react.md")
#         system_prompt = template.render(**state_vars)
#         return system_prompt

#     def format(self, **kwargs):
#         pass


def render_base_prompt_tpl(prompt_name: str, state: AgentState) -> str:
    """
    Render a base prompt template.

    Args:
        prompt_name: Name of the base prompt template to render

    Returns:
        Rendered base prompt template as a string
    """
    base_prompt = render_prompt_template(prompt_name, state)
    return BasePromptTemplate(
        input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
        template=base_prompt,
    )


def render_prompt_template(prompt_name: str, state: AgentState) -> str:
    """
    Render a prompt template with the given state variables.

    Args:
        prompt_name: Name of the prompt template to render
        state: Current agent state containing variables to substitute

    Returns:
        Rendered prompt template as a string
    """
    # Convert state to dict for template rendering
    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state,
    }
    template = env.get_template(f"{prompt_name}.md")
    system_prompt = template.render(**state_vars)
    return system_prompt


def apply_prompt_template(prompt_name: str, state: AgentState) -> list:
    """
    Apply template variables to a prompt template and return formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        state: Current agent state containing variables to substitute

    Returns:
        List of messages with the system prompt as the first message
    """

    try:
        system_prompt = render_prompt_template(prompt_name, state)
        return [{"role": "system", "content": system_prompt}] + (state['messages'] if 'messages' in state else [])
    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {e}")


if __name__ == "__main__":
    print(
        render_prompt_template(
            "react",
            AgentState(
                tools=[tavily_search, arxiv_search],
                tool_names=["tavily_search", "arxiv_search"],
            ),
        )
    )
