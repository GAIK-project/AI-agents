import os
from typing import Any, Dict, List, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from swarm import Agent, Swarm

# Load environment variables
load_dotenv()

# Define Result class


class Result:
    """A class for returning multiple values from a function."""

    def __init__(self, value=None, agent=None, context_variables=None):
        self.value = value
        self.agent = agent
        self.context_variables = context_variables or {}


# Initialize FastAPI app
app = FastAPI(title="Swarm Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Swarm client
client = Swarm()

# Agent functions


def transfer_to_finnish():
    """Transfer the conversation to the Finnish-speaking agent."""
    print("Transferring to Finnish-speaking agent...")
    return finnish_agent


def transfer_to_weather():
    """Transfer the conversation to the weather agent."""
    print("Transferring to weather agent...")
    return weather_agent


def update_user_info(context_variables, name, location=None):
    """Update user information in context variables."""
    new_context = {"user_name": name}
    if location:
        new_context["location"] = location

    print(f"Updated user info: {name} from {location}")
    print(f"Current context: {context_variables}")

    # Create new context that includes current and new values
    result_context = {**context_variables, **new_context}
    print(f"Updated context: {result_context}")

    return Result(
        value=f"Updated your information: {name} from {location or 'unknown location'}",
        context_variables=result_context
    )


# Main agent
main_agent = Agent(
    name="Assistant",
    model="gpt-4o",
    instructions=lambda context_variables: f"""You are a helpful assistant.
If the user wants to speak in Finnish or mentions Finland, transfer to the Finnish-speaking agent using transfer_to_finnish().
If the user asks about weather information, transfer to the weather agent using transfer_to_weather().
You can update user information using the update_user_info function.
Current user info: {context_variables.get('user_name', 'Unknown')} from {context_variables.get('location', 'Unknown location')}

When user asks to update their information or change their name or location, use the update_user_info function with appropriate parameters.
""",
    functions=[transfer_to_finnish, transfer_to_weather, update_user_info]
)

# Function for Finnish agent


def transfer_to_assistant():
    """Transfer back to the main assistant agent."""
    print("Returning to main assistant...")
    return main_agent


# Finnish agent
finnish_agent = Agent(
    name="Finnish Agent",
    model="gpt-4o",
    instructions=lambda context_variables: f"""You are a helpful agent who speaks ONLY in Finnish.
Always respond in Finnish, regardless of the language the user is using.
Current user: {context_variables.get('user_name', 'friend')} from {context_variables.get('location', 'somewhere')}
If the user wants to stop speaking Finnish, transfer them back to the main assistant using transfer_to_assistant().
""",
    functions=[transfer_to_assistant]
)

# Weather agent function


def get_weather(location=None):
    """Get weather information for a location."""
    if not location:
        location = "Helsinki"

    # Simple weather data
    weather_data = {
        "New York": "Sunny, 75°F",
        "London": "Rainy, 60°F",
        "Tokyo": "Cloudy, 70°F",
        "Sydney": "Clear, 80°F",
        "Helsinki": "Snow, 25°F (-4°C)",
    }

    weather = weather_data.get(
        location, f"Weather data not available for {location}")
    return f"The current weather in {location} is: {weather}"


# Weather agent
weather_agent = Agent(
    name="Weather Expert",
    model="gpt-4o",
    instructions=lambda context_variables: f"""You are a weather expert who helps users find weather information.
You have access to the get_weather function to check current conditions.
Current user: {context_variables.get('user_name', 'visitor')} from {context_variables.get('location', 'unknown location')}
If the user wants to discuss something other than weather, transfer them back to the assistant using transfer_to_assistant().
""",
    functions=[get_weather, transfer_to_assistant]
)

# Pydantic models for API


class SwarmRequest(BaseModel):
    messages: List[Dict[str, Any]]
    context_variables: Optional[Dict[str, Any]] = {}


@app.post("/api/swarm")
async def swarm_chat(request: SwarmRequest):
    try:
        # Log the request
        print(f"Received request with {len(request.messages)} messages")

        # Limit message count to avoid context issues
        if len(request.messages) > 10:
            request.messages = request.messages[-10:]
            print(f"Truncated to {len(request.messages)} messages")

        # Clean messages to the correct format
        clean_messages = []
        for msg in request.messages:
            if msg.get("role") in ["user", "assistant", "system"]:
                content = msg.get("content")
                if content is not None:
                    clean_messages.append({
                        "role": msg.get("role"),
                        "content": content
                    })

        # Ensure there's at least one message
        if not clean_messages:
            clean_messages = [{"role": "user", "content": "Hello"}]

        # Get context variables
        context = request.context_variables or {}
        print(f"Context variables: {context}")

        # Identify current agent
        current_agent = main_agent
        for msg in reversed(request.messages):
            if msg.get("sender") == "Finnish Agent":
                current_agent = finnish_agent
                break
            elif msg.get("sender") == "Weather Expert":
                current_agent = weather_agent
                break

        print(f"Using agent: {current_agent.name}")

        # Run the Swarm client
        response = client.run(
            agent=current_agent,
            messages=clean_messages,
            context_variables=context,
            stream=False
        )

        print(
            f"Got response from Swarm with {len(response.messages)} messages")
        print(f"Response agent: {response.agent.name}")
        print(f"Response context: {response.context_variables}")

        # Return formatted response
        return {
            "messages": response.messages,
            "agent_name": response.agent.name,
            "context_variables": response.context_variables
        }

    except Exception as e:
        print(f"Error: {str(e)}")

        # Return a simple response in error cases
        return {
            "messages": request.messages + [{
                "role": "assistant",
                "content": "I'm sorry, I encountered an error. Could you try again?",
                "sender": "Assistant"
            }],
            "agent_name": "Assistant",
            "context_variables": request.context_variables or {}
        }

# Run the app
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
