from src.graph.nodes import Nodes
from langgraph.graph import END, StateGraph
from src.graph.states import State


workflow = StateGraph(State)

workflow.add_node("agent_search", Nodes.node_search_agent)
workflow.add_node("agent_writer", Nodes.node_writer_agent)
workflow.add_node("tool_node", Nodes.tool_node)

workflow.set_entry_point("agent_search")

workflow.add_conditional_edges(
    "agent_search",
    Nodes.should_continue,
    ["tool_node", "agent_writer"]
)

workflow.add_edge("tool_node", "agent_search")
workflow.add_edge("agent_writer", END)

graph = workflow.compile()

def visualize_graph():
    from IPython.display import Image, display
    display(Image(graph.get_graph(xray=True).draw_mermaid_png()))