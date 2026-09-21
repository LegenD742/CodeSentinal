"""
Wires all nodes into the LangGraph StateGraph:

    supervisor (specialist agents, parallel) -> critic -> aggregator -> commenter

This linear-looking graph hides real parallelism inside the supervisor
node (every hunk x agent pair runs concurrently) and gives us a clean
place to add more stages later (e.g. a re-analysis loop if the critic
rejects too much).
"""
from langgraph.graph import END, StateGraph

from app.graph.aggregator_node import aggregator_node
from app.graph.commenter_node import commenter_node
from app.graph.critic_node import critic_node
from app.graph.state import ReviewState
from app.graph.supervisor_node import specialist_agents_node


def build_review_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("specialist_agents", specialist_agents_node)
    graph.add_node("critic", critic_node)
    graph.add_node("aggregator", aggregator_node)
    graph.add_node("commenter", commenter_node)

    graph.set_entry_point("specialist_agents")
    graph.add_edge("specialist_agents", "critic")
    graph.add_edge("critic", "aggregator")
    graph.add_edge("aggregator", "commenter")
    graph.add_edge("commenter", END)

    return graph.compile()


review_graph = build_review_graph()
