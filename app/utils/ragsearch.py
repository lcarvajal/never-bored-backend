from tavily import TavilyClient
import os

tavily_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=tavily_key)


def get_search_resources(query: str):
    return tavily_client.search(query)
