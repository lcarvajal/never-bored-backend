from tavily import TavilyClient
import os

tavily_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=tavily_key)

def get_search_resources(learning_topic: str):
  prompt = "Give me resources on `" + learning_topic + "`"
  
  return tavily_client.search(prompt)