import os

from dotenv import load_dotenv
from smolagents import (CodeAgent, DuckDuckGoSearchTool, HfApiModel,
                        LiteLLMModel)

# Load environment variables from .env file
load_dotenv()
# Get the token and authenticate
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the model with the token
model = LiteLLMModel(model_id="gpt-4o-mini")  # or gpt-3.5-turbo
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

if __name__ == "__main__":
    result = agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?")
    print(result)