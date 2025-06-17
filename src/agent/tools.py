
from typing import Callable, Any
from loguru import logger
import functools
from langchain_core.tools import tool
from src.conf.config_loader import config_data
from langchain_tavily import TavilySearch

def log_io(func: Callable) -> Callable:
    """
    A decorator that logs the input parameters and output of a tool function.

    Args:
        func: The tool function to be decorated

    Returns:
        The wrapped function with input/output logging
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Log input parameters
        func_name = func.__name__
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.debug(f"Tool {func_name} called with parameters: {params}")

        # Execute the function
        result = func(*args, **kwargs)

        # Log the output
        logger.debug(f"Tool {func_name} returned: {result}")

        return result

    return wrapper

import os
os.environ["TAVILY_API_KEY"] = config_data['tavily']['key']
tavily_tool = TavilySearch(max_results=3)

@tool
@log_io
def tavily_search(query: str) -> str:
    """Searches for the query."""
    return tavily_tool.invoke(input=query)


from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper

arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper())

@tool
@log_io
def arxiv_search(query: str)->str:
    """Searches for the query in arxiv."""
    return arxiv_search.invoke(query)