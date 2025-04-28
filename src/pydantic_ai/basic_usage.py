from pydantic import BaseModel

from pydantic_ai import Agent


# Define a structured output model
class CityLocation(BaseModel):
    city: str
    country: str

# Create an agent with structured output
agent = Agent('openai:gpt-4o', result_type=CityLocation)

# Run the agent
result = agent.run_sync('Where were the olympics held in 2012?')
print(result.data)  # city='London' country='United Kingdom'