"""
Simple LangGraph Swarm Example - Fixed Version

This example creates a two-agent system with:
- A math expert (Alice)
- A creative writer (Bob)
"""

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

# Initialize language model (replace with your API key)
# export OPENAI_API_KEY=your_api_key
model = ChatOpenAI(model="gpt-4o")

# Create a simple math function for Alice
def calculate(expression: str) -> float:
    """Evaluate a mathematical expression"""
    return eval(expression)

# Create Alice - the math expert
alice = create_react_agent(
    model,
    [
        calculate, 
        create_handoff_tool(agent_name="Bob", description="Transfer to Bob for creative writing")
    ],
    prompt="You are Alice, a mathematics expert. You can solve calculations using the calculate tool.",
    name="Alice",
)

# Create Bob - the creative writer
bob = create_react_agent(
    model,
    [
        create_handoff_tool(agent_name="Alice", description="Transfer to Alice for mathematical calculations")
    ],
    prompt="You are Bob, a creative writer who specializes in storytelling and poetry.",
    name="Bob",
)

# Create short-term memory
checkpointer = InMemorySaver()

# Create the swarm workflow
workflow = create_swarm(
    [alice, bob],
    default_active_agent="Alice"  # Start with Alice by default
)

# Compile the workflow
app = workflow.compile(checkpointer=checkpointer)

# Example usage
def run_example():
    config = {"configurable": {"thread_id": "example1"}}
    
    # First interaction
    print("User: Can you help me solve 25 * 16?")
    response1 = app.invoke(
        {"messages": [{"role": "user", "content": "Can you help me solve 25 * 16?"}]},
        config,
    )
    print_simple_response(response1)
    
    # Second interaction
    print("\nUser: Now I'd like to speak with Bob about writing a short poem")
    response2 = app.invoke(
        {"messages": [{"role": "user", "content": "Now I'd like to speak with Bob about writing a short poem"}]},
        config,
    )
    print_simple_response(response2)
    
    # Third interaction
    print("\nUser: Write a poem about mathematics")
    response3 = app.invoke(
        {"messages": [{"role": "user", "content": "Write a poem about mathematics"}]},
        config,
    )
    print_simple_response(response3)

def print_simple_response(response):
    """Very simple response printer that just shows active agent and last AI message"""
    # Get active agent
    active_agent = "Unknown"
    if "active_agent" in response:
        active_agent = response["active_agent"]
    
    # Get messages and find the last AI message
    if "messages" in response:
        messages = response["messages"]
        for msg in reversed(messages):
            # Check for AI message by type attribute
            if hasattr(msg, "type") and msg.type == "ai":
                print(f"\n{active_agent} says: {msg.content}\n")
                return
    
    print("No response found")

if __name__ == "__main__":
    run_example()