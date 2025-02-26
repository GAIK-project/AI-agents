# Structured Data Agent

A LangGraph-based application that extracts structured data from natural language text with human feedback capabilities.

## Overview

This application uses LangGraph to create a workflow that:

1. Extracts structured information from user input
2. Asks for user feedback on the extracted data
3. Regenerates the data if the user is not satisfied, incorporating their feedback
4. Finalizes the structured data once the user accepts it

The agent produces structured data with a consistent schema including data type, primary entity, attributes, dates, tags, and more.

## Project Structure

```
src/
├── __init__.py
├── graph.py        # LangGraph workflow definition
├── nodes.py        # Node implementations
├── schemas.py      # Pydantic data models
└── state.py        # State definition
main.py             # CLI interface
```

## Requirements

- Python 3.8+
- LangGraph
- LangChain
- OpenAI API key

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd structured-data-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_openai_key_here
```

## Usage

### CLI Demo

To run the agent in command-line mode:

```bash
python main.py
```

Follow the prompts to:

1. Enter natural language text
2. Review the extracted structured data
3. Accept the data or provide feedback for improvements
4. Receive the final structured data

### API Integration (Future)

The agent is designed to be easily integrated with a FastAPI backend and a React frontend. The human-in-the-loop feedback mechanism maps well to API endpoints.

## Customization

To extend or modify the structured data schema, edit the `StructuredData` class in `schemas.py`.

## How It Works

1. The agent uses a state machine architecture with LangGraph
2. The `generate_structured_data` node extracts structured data from user input
3. The `get_human_feedback` node interrupts execution to get user feedback
4. Based on feedback, the workflow either regenerates data or finalizes it
5. All state is persisted using LangGraph's checkpointing system

## License

MIT