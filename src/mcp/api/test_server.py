# test_server.py
import requests

# You will get this URL by starting mini.py script. See "MCP Server available at:<URL>"
url = "https://a2d7-193-166-15-251.ngrok-free.app/sse"  # Replace with your ngrok URL

try:
    response = requests.get(url, stream=True)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Server is working!")
except Exception as e:
    print(f"Error connecting to server: {e}")
    