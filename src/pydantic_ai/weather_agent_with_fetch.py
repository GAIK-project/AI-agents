import asyncio
import os  # Import the 'os' module
from dataclasses import dataclass
from typing import Optional

import httpx
from dotenv import load_dotenv  # Import load_dotenv

from pydantic_ai import Agent, RunContext

# Load environment variables from .env file
load_dotenv()

# Note: You need weatherapi.com API key to run this example. Set it to .env file as WEATHERAPI_KEY

# 1. Define your dependencies structure
@dataclass
class WeatherDeps:
    api_key: str
    http_client: httpx.AsyncClient
    
    # Helper method to fetch weather data
    async def get_weather(self, city: str) -> dict:
        url = f"https://api.weatherapi.com/v1/current.json"
        params = {"key": self.api_key, "q": city}
        response = await self.http_client.get(url, params=params)
        response.raise_for_status()
        return response.json()

# 2. Create an agent with these dependencies
weather_agent = Agent(
    'openai:gpt-4o',
    deps_type=WeatherDeps,  # Tell the agent what type of dependencies to expect
    system_prompt="You provide weather information based on real-time data."
)

# 3. Create a tool that uses the dependencies to fetch external data
@weather_agent.tool
async def fetch_weather(ctx: RunContext[WeatherDeps], city: str) -> str:
    """Fetch current weather for the specified city."""
    try:
        # Access the dependencies through ctx.deps
        weather_data = await ctx.deps.get_weather(city)
    
        # Extract relevant information
        location = weather_data["location"]["name"]
        country = weather_data["location"]["country"]
        temp_c = weather_data["current"]["temp_c"]
        condition = weather_data["current"]["condition"]["text"]
        print(f"Featched: Weather in {location}, {country}: {temp_c}°C, {condition}")
        return f"Weather in {location}, {country}: {temp_c}°C, {condition}"
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

# 4. Use the agent with properly initialized dependencies
async def main():
    # Create HTTP client
    async with httpx.AsyncClient() as client:
        # Get the API key from the environment variable
        api_key = os.getenv("WEATHERAPI_KEY")  # Replace "WEATHERAPI_KEY" with the actual name of your environment variable

        # Initialize dependencies with your API key and the HTTP client
        deps = WeatherDeps(
            api_key=api_key,
            http_client=client
        )
        
        # Run the agent with these dependencies
        result = await weather_agent.run(
            "What's the weather like in Helsinki today?",
            deps=deps  # Pass the dependencies to the agent
        )
        
        print(result.data)


if __name__ == "__main__":
    asyncio.run(main())