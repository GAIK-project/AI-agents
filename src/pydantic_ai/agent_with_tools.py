import random

from pydantic_ai import Agent, RunContext

agent = Agent(
    'anthropic:claude-3-5-sonnet-latest',
    system_prompt="You're a dice game. Roll the die and check if it matches the user's guess."
)

@agent.tool_plain
def roll_die() -> str:
    """Roll a six-sided die and return the result."""
    return str(random.randint(1, 6))

@agent.tool
def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name."""
    return ctx.deps

result = agent.run_sync('My guess is 4', deps='Anna')
print(result.data)