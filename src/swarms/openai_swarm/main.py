from dotenv import load_dotenv
from swarm import Agent, Swarm

load_dotenv()


# Define our own Result class if not available in the swarm package
class Result:
    """A class for returning multiple values from a function."""

    def __init__(self, value=None, agent=None, context_variables=None):
        self.value = value
        self.agent = agent
        self.context_variables = context_variables or {}


# Initialize the Swarm client
client = Swarm()

# Define specialized agents

# Main assistant agent


def transfer_to_finnish():
    """Transfer the conversation to the Finnish-speaking agent."""
    print("Siirretään keskustelu suomenkieliselle agentille...")
    return finnish_agent


def transfer_to_weather():
    """Transfer the conversation to the weather agent."""
    print("Transferring to weather agent...")
    return weather_agent


def update_user_info(context_variables, name, location=None):
    """Update user information in the context variables.

    Args:
        context_variables: Current context variables - required by Swarm framework.
        name: Name of the user.
        location: Location of the user.
    """
    # Note: context_variables parameter is required by the Swarm framework
    # The framework injects this parameter automatically when calling the function

    new_context = {"user_name": name}
    if location:
        new_context["location"] = location

    print(f"Updated user info: {name} from {location}")
    print(f"Context after update: Name: {name}  Location: {location}")
    return Result(
        value="User information updated successfully.",
        context_variables=new_context
    )


main_agent = Agent(
    name="Assistant",
    model="gpt-4o",
    instructions=lambda context_variables: f"""You are a helpful assistant.
If the user wants to speak in Finnish or mentions Finland, transfer to the Finnish-speaking agent.
If the user asks about weather information, transfer to the weather agent.
You can update user information using the update_user_info function.
Current user info: {context_variables.get('user_name', 'Unknown')} from {context_variables.get('location', 'Unknown location')}
""",
    functions=[transfer_to_finnish, transfer_to_weather, update_user_info]
)

# Finnish agent that speaks in Finnish


def transfer_to_assistant():
    """Transfer back to the main assistant agent."""
    print("Palataan takaisin pääassistenttiin...")
    return main_agent


finnish_agent = Agent(
    name="Finnish Agent",
    model="gpt-4o",
    instructions=lambda context_variables: f"""You are a helpful agent who speaks ONLY in Finnish.
Always respond in Finnish, regardless of the language the user is using.
Current user: {context_variables.get('user_name', 'friend')} from {context_variables.get('location', 'somewhere')}
If the user wants to stop speaking Finnish, transfer them back to the main assistant.
""",
    functions=[transfer_to_assistant]
)

# Weather agent for weather information


def get_weather(location=None):
    """Get the weather for a location.

    Args:
        location: The location to get weather for.
    """
    if not location:
        return "Please specify a location to check the weather."

    # This would be a real API call in a production system
    weather_data = {
        "New York": "Sunny, 75°F",
        "London": "Rainy, 60°F",
        "Tokyo": "Cloudy, 70°F",
        "Sydney": "Clear, 80°F",
        "Helsinki": "Snow, 25°F",
    }

    weather = weather_data.get(
        location, f"Weather data not available for {location}")
    return f"The current weather in {location} is: {weather}"


weather_agent = Agent(
    name="Weather Expert",
    model="gpt-4o",
    instructions=lambda context_variables: f"""You are a weather expert who helps users find weather information.
You have access to the get_weather function to check current conditions.
Current user: {context_variables.get('user_name', 'visitor')} from {context_variables.get('location', 'unknown location')}
If the user wants to discuss something other than weather, transfer them back to the assistant.
""",
    functions=[get_weather, transfer_to_assistant]
)

# Function to run a simple demo


def run_demo():
    from swarm.repl import run_demo_loop

    print("Starting Swarm Agent Demo...")
    print("You can talk to the assistant, ask for Finnish help, or check weather.")
    print("Type 'exit' to quit.")
    print("-" * 50)

    # Initialize with some context variables
    initial_context = {"user_name": "Guest", "location": "Unknown"}

    # Run the interactive demo loop
    # The first argument should be positional, not a keyword argument
    run_demo_loop(
        main_agent,
        context_variables=initial_context,
        stream=True
    )

# Run the demo if this script is executed directly
if __name__ == "__main__":
    run_demo()
