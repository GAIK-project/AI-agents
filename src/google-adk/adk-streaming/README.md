# ADK Streaming Quickstart

## Overview

Google ADK Streaming enables real-time interactive AI agents with bidirectional communication.

## Quick Steps

1. **Setup**: Create virtual env, install Google-ADK
2. **Structure**: Create project with app folder, main.py, static/index.html
3. **API Key**: Add .env file with Google API key
4. **Test**: Run `adk web` to test with built-in tool
5. **Custom App**: Build FastAPI app with WebSockets for streaming communication

## Running

```bash
cd app
uvicorn main:app --reload
```

Access UI: http://localhost:8000

Docs: https://google.github.io/adk-docs/get-started/quickstart-streaming/
