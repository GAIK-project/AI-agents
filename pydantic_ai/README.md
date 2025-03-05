# Pydantic-AI

A strongly typed framework for building AI agents and complex workflows with LLMs in Python.

## Features

- **Model Agnostic:** Works with OpenAI, Anthropic, Google, Mistral, Groq, and more
- **Type Safe:** Leverages Python type hints for schema and validation
- **Function Tools:** Allow agents to access external information
- **Structured Outputs:** Define exact schemas for the data you want returned
- **Dependency Injection:** Share resources between different components
- **Streaming Support:** Stream responses as they're generated
- **Graph Workflows:** Build complex stateful workflows with pydantic-graph

## Installation

```bash
pip install pydantic-ai  # Full installation
# OR
pip install 'pydantic-ai-slim[openai,anthropic]'  # Minimal with specific providers
```

## Quick Example

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class MovieRecommendation(BaseModel):
    title: str
    year: int
    reason: str

agent = Agent('anthropic:claude-3-5-sonnet-latest', result_type=MovieRecommendation)
result = agent.run_sync('Recommend a sci-fi movie')
print(result.data)
```

## Repository Examples

This repository contains several example implementations of Pydantic-AI:

### basic_usage.py

Demonstrates the fundamentals of creating an agent with structured output. This example shows how to define a Pydantic model for structured data and have an LLM agent extract information into that format.

### agent_with_tools.py

Shows how to enhance an agent with function tools. This example implements a simple dice game where an agent calls tools to roll dice and get player information, demonstrating how LLMs can interact with external functions.

### weather_agent_with_fetch.py

Illustrates dependency injection by creating a weather agent that fetches real-time data from an external API. This example shows how to properly structure and pass external resources (API clients, credentials) to an agent.

### agent_with_graph.py

Demonstrates advanced workflow orchestration using pydantic-graph. This example shows how to build complex, stateful conversation flows where multiple steps are coordinated in a finite state machine pattern.

## Dependencies

See `requirements.txt` for all required packages.

## Documentation

Full documentation available at [https://github.com/pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai)

## License

MIT
