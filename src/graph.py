"""Graph definition for the LangGraph agent."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.nodes import (generate_structured_data, get_human_feedback,
                       process_structured_data)
from src.state import State

# Create graph builder
graph_builder = StateGraph(State)

# Add nodes to the graph
graph_builder.add_node("generate_structured_data", generate_structured_data)
graph_builder.add_node("get_human_feedback", get_human_feedback)
graph_builder.add_node("process_structured_data", process_structured_data)


# Define conditional routing based on user feedback
def route_based_on_feedback(state: State):
    """Route to next node based on human feedback.

    Args:
        state: Current application state

    Returns:
        str: Name of the next node
    """
    # Check if "is_satisfied" is present in the state
    if "is_satisfied" not in state:
        return "generate_structured_data"

    # Route based on satisfaction flag
    if state["is_satisfied"] is True:
        # If user is satisfied, proceed to processing
        return "process_structured_data"
    else:
        # If user is not satisfied, try again
        return "generate_structured_data"


# Add edges between nodes
graph_builder.add_edge("generate_structured_data", "get_human_feedback")
graph_builder.add_conditional_edges(
    "get_human_feedback", route_based_on_feedback
)
graph_builder.add_edge("process_structured_data", END)

# Set the entry point
graph_builder.set_entry_point("generate_structured_data")

# Create memory saver for state persistence
memory = MemorySaver()

# Compile the graph with checkpointing
graph = graph_builder.compile(checkpointer=memory)
