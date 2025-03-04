# Swarm Agent Framework

## Overview

Swarm is an experimental, educational framework developed by OpenAI for exploring ergonomic, lightweight multi-agent orchestration. It provides a clean, intuitive interface for building and coordinating multiple AI agents.

> **Warning**: Swarm is currently experimental and intended for educational purposes. It is not designed for production use and has no official support.

## Core Features

- **Lightweight Agent Coordination**: Simple primitives for agent creation and handoffs
- **Function Integration**: Direct Python function calling with automatic schema generation
- **Context Management**: Maintain and update context variables across agent interactions
- **Agent Handoffs**: Seamless conversation transfer between specialized agents
- **Streaming Support**: Real-time response streaming capabilities

## Basic Usage

```python
from swarm import Swarm, Agent

# Initialize client
client = Swarm()

# Define agent transfer function
def transfer_to_agent_b():
    return agent_b

# Create agents
agent_a = Agent(
    name="Agent A",
    instructions="You are a helpful agent.",
    functions=[transfer_to_agent_b],
)

agent_b = Agent(
    name="Agent B",
    instructions="Only speak in Haikus.",
)

# Run conversation
response = client.run(
    agent=agent_a,
    messages=[{"role": "user", "content": "I want to talk to agent B."}],
)
```

## Why Use Swarm?

Swarm is ideal for situations dealing with multiple specialized capabilities that would be difficult to encode in a single prompt. The framework allows for:

- Building networks of specialized agents
- Defining clean workflows with explicit handoffs
- Maintaining control over conversation state
- Testing and evaluating multi-agent systems

## Installation

```bash
pip install git+https://github.com/openai/swarm.git
```

## Requirements

- Python 3.10+
- OpenAI API key (set as environment variable)

## Further Reading

For more detailed documentation and examples, visit the [Swarm GitHub repository](https://github.com/openai/swarm).
