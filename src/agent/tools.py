from typing import Callable, Any
from loguru import logger
import functools
from langchain_core.tools import tool
from src.conf.config_loader import config_data
from langchain_tavily import TavilySearch
from firecrawl import FirecrawlApp
from typing import Annotated
import os

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


os.environ["TAVILY_API_KEY"] = config_data["tavily"]["key"]
tavily_tool = TavilySearch(max_results=config_data["tavily"]["max_results"])


@tool
@log_io
def tavily_search(query: str) -> str:
    """Search web pages related to the query in internet."""
    return tavily_tool.invoke(input=query)


from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper

arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper())


@tool
@log_io
def arxiv_search(query: str) -> str:
    """Searches papers related to the query in arxiv."""
    return arxiv_search.invoke(query)

os.environ['FIRECRAWL_API_KEY'] = config_data['firecrawl']['key']

@tool
@log_io
def web_crawl(url: str) -> str:
    """
    Crawl a website and return the markdown content.

    Args:
        url: The URL of the website to crawl.

    Returns:
        The markdown content of the website.
    """
    firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = firecrawl.scrape_url(
        url=url, formats=["markdown"], only_main_content=True
    )
    return response.markdown


@tool
def handoff_to_planner(
    research_topic: Annotated[str, "The topic of the research task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to planner agent to do plan."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    return
