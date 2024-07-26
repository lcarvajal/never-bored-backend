from tavily import TavilyClient
import os

tavily_key = os.getenv("TAVILY_API_KEY")
print("WHAT IS GOING ON HERE")
print(tavily_key)
print(os)
tavily_client = TavilyClient(api_key=tavily_key)

def get_search_resources(learning_topic: str):
  prompt = "Give me resources on `" + learning_topic + "`"
  
  return tavily_client.search(prompt)