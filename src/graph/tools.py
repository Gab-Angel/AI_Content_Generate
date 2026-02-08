from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from tavily import TavilyClient
from src.agent.agents import llm
from dotenv import load_dotenv
import os

load_dotenv()

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

class Tools:
    @tool(description="""
        Pesquisa informações na web sobre o topic e idea fornecidos.
        
        Args:
            query: Query detalhada combinando topic + idea para busca eficiente.
        
        Returns:
            Resultados da pesquisa com answer e snippets.
        """)
    def web_search(query: str) -> dict:
        
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            search_depth='advanced',
            topic="news",
            days=30,
            max_results=2,
            include_answer=True,
            include_raw_content=False
        )

        return {
            'answer': response.get('answer', ''),
            'results': [
                {
                    'title': r['title'],
                    'url': r['url'], 
                    'content': r['content']
                }
                for r in response.get('results', [])
            ]
        }
    
    tool_search = [web_search]
    tool_node = ToolNode(tool_search)
    llm_with_tools = llm.bind_tools(tool_search)