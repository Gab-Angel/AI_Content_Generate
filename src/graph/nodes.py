from src.graph.states import State
from typing import Literal
from src.graph.tools import Tools
from src.agent.agents import search_agent, writer_agent

class Nodes:
    @staticmethod
    def node_search_agent(state: State):
        return search_agent(
            state=state,
            llm_model=Tools.llm_with_tools
        )
    
    @staticmethod
    def node_writer_agent(state: State):
        return writer_agent(
            state=state,
            llm_model=Tools.llm_with_tools
        )
    
    @staticmethod
    def should_continue(state: State) -> Literal["tool_node", "agent_writer"]:
        messages = state.messages
        
        if not messages:
            return "agent_writer"
        
        last_message = messages[-1]
        
        # Se tem tool_calls, executa tools
        if getattr(last_message, 'tool_calls', None):
            return "tool_node"
        
        return "agent_writer"
    
    @staticmethod
    def tool_node(state: State):
        # ToolNode já processa automaticamente
        return Tools.tool_node.invoke({"messages": [state.messages[-1]]})