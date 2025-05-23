# test_with_anthropic.py
import os

import anthropic
from dotenv import load_dotenv

# Load environment variables and make sure it works
load_dotenv()
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

# Create client with explicit API key
client = anthropic.Anthropic(api_key=api_key)

def call_llm() -> None:
    # First, ensure mini.py is running in another terminal with:
    # python mini.py
    # This will start the server and give you a URL to use
    # You will get this URL by starting mini.py script. See "MCP Server available at:<URL>"
    
    response = client.beta.messages.create(
        model="claude-3-7-sonnet-latest",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": "Use the calculate tool to multiply 50 * 3"
        }],
        mcp_servers=[{
            "type": "url",
            "url": "https://a2d7-193-166-15-251.ngrok-free.app/sse",  # Replace with your ngrok URL from mini.py
            "name": "calc"
        }],
        betas=["mcp-client-2025-04-04"]
    )

    print(response.content)

if __name__ == "__main__":
    call_llm()