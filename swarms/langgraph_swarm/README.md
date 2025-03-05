# LangGraph Swarm

LangGraph Swarm is a specialized extension for LangGraph that enables creating swarm-style multi-agent systems with minimal setup. It allows multiple AI agents to collaborate by dynamically handing off tasks to one another based on their specializations.

## Installation

```bash
pip install langgraph-swarm
```

## Built On

This library is built on top of LangGraph, a powerful framework for building agent applications that supports:

- Streaming responses
- Short-term and long-term memory
- Human-in-the-loop capabilities

## Requirements

- Python 3.8+
- LangChain
- LangGraph

See the example main.py code and documentation for more detailed implementation instructions.
[LangGraph Swarm - GitHub Repository](https://github.com/langchain-ai/langgraph-swarm-py)
[main.py Example](./main.py)

## Minimal Implementation

```python
# Create agents with their specializations
math_agent = create_react_agent(model, [math_tools, create_handoff_tool(agent_name="writing_agent")])
writing_agent = create_react_agent(model, [writing_tools, create_handoff_tool(agent_name="math_agent")])

# Create the swarm with just one line
workflow = create_swarm([math_agent, writing_agent], default_active_agent="math_agent")

# Compile with memory
app = workflow.compile(checkpointer=InMemorySaver())
```

The true power of LangGraph Swarm is that it simplifies complex multi-agent interactions that would otherwise require significant boilerplate code and careful state management in standard LangGraph implementations.
