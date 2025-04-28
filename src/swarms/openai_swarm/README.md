# Swarm Agent Framework

## Overview

Swarm is an experimental, educational framework developed by OpenAI for exploring lightweight multi-agent orchestration. It provides an intuitive interface for building and coordinating multiple AI agents through simple primitives.

> **Warning**: Swarm is currently experimental and intended for educational purposes. It is not designed for production use.

## Core Features

- **Lightweight Agent Coordination**: Simple primitives for agent creation and handoffs
- **Function Integration**: Direct Python function calling with automatic schema generation
- **Context Management**: Maintain and update context variables across agent interactions
- **Agent Handoffs**: Seamless conversation transfer between specialized agents
- **Streaming Support**: Real-time response streaming capabilities

## Basic Usage

```python
from dotenv import load_dotenv
from swarm import Agent, Swarm

# Load environment variables
load_dotenv()

# Initialize client
client = Swarm()

# Define an agent transfer function
def transfer_to_weather():
    """Transfer the conversation to the weather agent."""
    return weather_agent

# Create main assistant agent
main_agent = Agent(
    name="Assistant",
    model="gpt-4o",
    instructions=lambda context_variables: f"""You are a helpful assistant.
If the user asks about weather information, transfer to the weather agent.
Current user: {context_variables.get('user_name', 'Unknown')}""",
    functions=[transfer_to_weather]
)

# Define a function for the weather agent
def get_weather(location=None):
    """Get weather information for a location."""
    if not location:
        location = "Helsinki"

    weather_data = {
        "New York": "Sunny, 75°F",
        "Helsinki": "Snow, 25°F (-4°C)",
    }

    return f"The current weather in {location} is: {weather_data.get(location, 'unavailable')}"

# Create weather agent
weather_agent = Agent(
    name="Weather Expert",
    model="gpt-4o",
    instructions="You are a weather expert who helps users find weather information.",
    functions=[get_weather]
)

# Run a conversation
response = client.run(
    agent=main_agent,
    messages=[{"role": "user", "content": "What's the weather in New York?"}],
    context_variables={"user_name": "Alex"}
)
```

## Requirements

- Python 3.10+
- OpenAI API key (set as environment variable)

## Further Reading

For more detailed documentation and examples, visit the [Swarm GitHub repository](https://github.com/openai/swarm).
