# smolagents

A lightweight framework for building AI agents that can use tools and execute code to solve tasks.

## Overview

smolagents is an open-source framework developed by Hugging Face that allows you to build AI agents powered by various language models. These agents can:

- Execute Python code to solve problems
- Use specialized tools like web search, file processing, etc.
- Work together in hierarchical multi-agent systems
- Run securely with code isolation options

## Key Features

- **Multiple model support**: Works with models from Hugging Face, OpenAI, Azure, LiteLLM, MLX, and more
- **Code execution**: Agents can write and execute Python code to solve tasks
- **Tool integration**: Comes with built-in tools and easy integration of custom tools
- **Multi-agent systems**: Build hierarchical agent systems for complex tasks
- **Security options**: Run code locally with restrictions or in fully sandboxed environments

## Quick Start

```python
from smolagents import CodeAgent, HfApiModel

# Create a model and agent
model = HfApiModel()  # Uses a default free model
agent = CodeAgent(tools=[], model=model, add_base_tools=True)

# Run the agent on a task
agent.run("What would be the 100th Fibonacci number?")
```

## Security

smolagents offers two execution environments:

1. **Local Python Interpreter**: Default option that restricts imports, limits operations, and prevents dangerous code execution
2. **E2B Sandboxed Environment**: Maximum security option that runs code in an isolated container

## Documentation

- [Guided Tour](https://huggingface.co/docs/smolagents/guided_tour)
- [Tools Documentation](https://huggingface.co/docs/smolagents/tools)
- [Code Security](https://huggingface.co/docs/smolagents/tutorials/secure_code_execution)

## Links

- [GitHub Repository](https://github.com/huggingface/smolagents)
- [Hugging Face Documentation](https://huggingface.co/docs/smolagents)
