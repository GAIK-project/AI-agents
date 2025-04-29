# AI Agents Repository

This repository contains a collection of various Python-based AI agents implementing different architectures and capabilities.

## Package Management

This repository uses [Poetry](https://python-poetry.org/) for dependency management. Poetry provides a modern way to manage Python packages with automatic dependency resolution and virtual environment management.

### Using UV

[UV](https://github.com/astral-sh/uv) is an extremely fast Python package installer and resolver, written in Rust, designed as a drop-in replacement for `pip` and `pip-tools`. You can use it with Poetry projects as well.

First, ensure you have `uv` installed. You can find installation instructions [here](https://github.com/astral-sh/uv#installation).

```bash
# Create a virtual environment using uv
uv venv

# Activate the environment
# On Windows:
.venv\Scripts\activate
# On Unix/MacOS:
source .venv/bin/activate

# Install dependencies using uv
uv pip install .

# Run the agent (example)
python swarms/openai_swarm/main.py
```

### Using Traditional Virtual Environments

You can also use traditional Python virtual environments if you prefer:

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

# Install dependencies from requirements.txt
# (if available in the agent directory)
pip install -r requirements.txt

# Run the agent
python main.py
````

## Available Agents

The repository includes the following agents:

1. **OpenAI Swarm Agent** - Multi-agent system with specialized roles that can transfer control between agents based on user needs. Includes Finnish language support and weather information capabilities.

   - `main.py`: Interactive CLI demo
   - `app.py`: FastAPI implementation with endpoints for integration

2. **Structured Data Agent** - LangGraph-based agent that extracts structured information from natural language with human feedback capabilities.
   - `main.py`: Interactive CLI demo

## API Endpoints

Some agents provide FastAPI endpoints that allow you to interact with them via HTTP requests. These are available in the respective `app.py` files:

- **OpenAI Swarm Agent API**:
  - Endpoint: `/api/swarm` (POST)
  - Run with: `poetry run uvicorn swarms.openai_swarm.app:app --reload`
  - Access the API docs at: `http://localhost:8000/docs`

To start any FastAPI server:

```bash
# From the repository root with Poetry
poetry run uvicorn <agent_folder>.app:app --reload

# Example
poetry run uvicorn swarms.openai_swarm.app:app --reload
```
