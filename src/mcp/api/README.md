# FastMCP - Quick Test Server

A simple MCP (Model Context Protocol) server for testing Claude API integration.

## Setup

1. Create a `.env` file with your API keys (see `.env.example`)
2. Install dependencies:
   ```bash
   pip install -e .
   ```

## 1. Start the server

```bash
python mini.py
```

The server will be available at:

- Locally: `http://127.0.0.1:8000/sse`
- Public (via ngrok): URL will be shown in the console

## 2. Test in browser

Open the URL in your browser. You should see an SSE stream start:

```
data: {"jsonrpc":"2.0","method":"..."}
```

## 3. Test with a simple Python script

```python
# test_server.py
import requests

# Check if server responds
response = requests.get("http://127.0.0.1:8000/sse", stream=True)
print(f"Status: {response.status_code}")
print("Server is working!")
```

## 4. Use with Anthropic Messages API

```python
# test_with_anthropic.py
import anthropic
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Use the remote server URL from ngrok
response = client.beta.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=[{
        "role": "user",
        "content": "Use the calculate tool with op='mul', a=50, b=3"
    }],
    mcp_servers=[{
        "type": "url",
        "url": "https://your-ngrok-url.ngrok-free.app/sse",  # Replace with your ngrok URL
        "name": "calc"
    }],
    betas=["mcp-client-2025-04-04"]
)

print(response.content)
```

## Summary

You can:

1. **Test the endpoint**: Server runs at `http://127.0.0.1:8000/sse`
2. **Use as MCP tool**: Messages API recognizes it immediately
3. **Deploy anywhere**: Works locally (with ngrok) or on cloud services

That's all you need - the server is ready to use as soon as it's running! 🚀

## Important Note on Tunneling

The Anthropic API cannot access `localhost` or `127.0.0.1` directly as these addresses only work on your local machine. This is why we use ngrok to create a public URL that Anthropic's servers can reach.

Without tunneling (using ngrok or similar), you'll get an error like:

```
Failed to connect to MCP server 'calc'. Please check the server URL and ensure the server is running.
```

For production use, you can deploy this server to cloud services like CSC Rahti 2 or similar platforms.
