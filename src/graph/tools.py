from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from tavily import TavilyClient
from src.agent.agents import llm_groq

from dotenv import load_dotenv
import os

load_dotenv()

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

class Tools:
    @tool('web_search',description="Use essa tool para inserir a query par realizar uma pesquisa")
    def web_search(query: str):

        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            max_results=1,
        )
        print('=======================================')
        print(response)
        print('=======================================')
        return response 
    

    tool_search = [
        web_search
    ]

    tool_node = ToolNode(tool_search)
    llm_with_tools = llm_groq.bind_tools(tool_search)