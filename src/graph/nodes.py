from langchain.messages import ToolMessage
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

        messages = state["messages"]
        last_message = messages[-1]

        if last_message.tool_calls:
            return "tool_node"

        return "agent_writer"
    
    @staticmethod
    def tool_node(state: dict):

        result = []
        for tool_call in state["messages"][-1].tool_calls:
            observation = Tools.tool_node.invoke(tool_call["args"])
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))

        return {"messages": result}