# mini.py
import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from pyngrok import ngrok

# Load environment variables
load_dotenv()

# Create and configure the server
mcp = FastMCP("Tools")

@mcp.tool()
def calculate(op: str, a: float, b: float) -> float:
    """Simple calculator: add/sub/mul/div"""
    ops = {"add": a+b, "sub": a-b, "mul": a*b, "div": a/b}
    return ops.get(op, 0)

# Set ngrok authentication token from environment variable
auth_token = os.environ.get("NGROK_AUTH_TOKEN")
if auth_token:
    ngrok.set_auth_token(auth_token)

# Create a tunnel to expose the local server
try:
    public_url = ngrok.connect("8000").public_url
    if public_url:
        sse_url = f"{public_url}/sse" if public_url.startswith('http') else f"https://{public_url}/sse"
        print(f"MCP Server available at: {sse_url}")
    else:
        print("Failed to establish ngrok connection: public_url is None")
except Exception as e:
    print(f"Error connecting to ngrok: {e}")

# Run the server
mcp.run(transport="sse", port=8000)