import random
from typing import Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext, RunUsage, Tool
from pydantic_ai.usage import UsageLimits

from utils import print_all_messages, show_metrics
from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Function tools with @agent.tool and @agent.tool_plain decorators
- Tool registration via Agent constructor with functions and Tool objects
- Context-aware tools using RunContext for dependency injection
- Tool schema generation with automatic parameter descriptions
- Usage metrics tracking (tokens, requests, tool calls)
- Usage limits and monitoring to prevent runaway costs
- Message history inspection to analyze tool interaction flows

This example demonstrates comprehensive tool usage and metrics tracking with Pydantic AI.
The example shows how tools extend agent capabilities beyond simple text generation,
enabling real-world integrations while maintaining control over resource usage through
different tool registration patterns and comprehensive monitoring capabilities.

For more details, visit:
https://ai.pydantic.dev/tools/
-----------------------------------------------------------------------------
"""

# --------------------------------------------------------------
# Example 1: Basic Tool Usage using decorators and with RunUsage
# --------------------------------------------------------------
print("=== Example 1: Basic Tool Usage ===")

# --- 1. Define the agent with the LLM ---
dice_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    deps_type=str,
    system_prompt=(
        "You're a dice game master. Roll the die and compare it to the user's guess. "
        "If they match, celebrate their win using their name!"
    ),
)


# --- 2. Define the custom tools ---
# 2.1 Using @tool_plain decorator for tools that don't require context
@dice_agent.tool_plain
def roll_dice() -> str:
    """Roll a six-sided die and return the result."""
    result = random.randint(1, 6)
    print(f"🎲 Die rolled: {result}")
    return str(result)


# 2.2 Using @tool decorator for tools that require context
@dice_agent.tool
def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name from the context."""
    return ctx.deps


# --- 3. Run the agent ---
dice_result = dice_agent.run_sync("My guess is 4", deps="Alice")
print(f"🎮 Game Result: {dice_result.output}")

# --- 4. Display usage metrics ---
usage: RunUsage = dice_result.usage
show_metrics(usage)  # from utils.py


# --------------------------------------------------------------
# Example 2: Advanced Tool Registration Patterns
# --------------------------------------------------------------
print("=== Example 2: Advanced Tool Registration Patterns and Usage Limits ===")


# --- 1. Define a Pydantic model for tool structured output ---
class WeatherData(BaseModel):
    """Weather information for a location."""

    temperature: int
    condition: str
    humidity: int


# --- 2. Define the custom tool with the structured output ---
def get_weather(location: str) -> WeatherData:
    """Get current weather for a location.

    Args:
        location: The city name to get weather for
    """
    # Simulate weather API call
    conditions = ["sunny", "cloudy", "rainy", "snowy"]
    return WeatherData(
        temperature=random.randint(-10, 35),
        condition=random.choice(conditions),
        humidity=random.randint(30, 90),
    )


# --- 3. Define the agent ---
# Method 1: Tools via Agent constructor with functions
weather_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    deps_type=Dict[str, Any],
    # pass the tool via Tool object
    tools=[
        Tool(get_weather, takes_ctx=False),  # No context needed
    ],
    # Alternatively, simply pass the tool like this
    # tools=[get_weather],
    system_prompt=(
        "You're a helpful weather assistant. "
        "Provide weather updates with the current time."
    ),
)

# --- 4. Run the agent ---
print("🌤️  Weather Agent:")
result = weather_agent.run_sync(
    "What's the weather in London?",
    deps={"user_location": "London"},  # Context dependencies
    usage_limits=UsageLimits(  # Set the usage limits for this run
        request_limit=5,
        tool_calls_limit=3,
    ),
)
print(f"   Response: {result.output}")
print(f"   Tool Calls: {result.usage.tool_calls} tool calls")
print("\n" + "=" * 60 + "\n")


# --------------------------------------------------------------
# Example 3: Message History and Tool Inspection
# --------------------------------------------------------------
print("=== Example 3: Message History and Tool Inspection ===")

# Create a more complex agent
research_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    system_prompt=("You're a database searcher. Only use the provided tools."),
)


@research_agent.tool_plain
def search_database(query: str) -> str:
    """Search a knowledge database.

    Args:
        query: The search query to look for
    """
    # Simulate database search
    if "ai" in query.lower():
        return "AI is cool"

    return "No relevant information found in database."


# Run research query and analyze message history
research_result = research_agent.run_sync("Tell me about AI")
print(f"🔍 Research Result: {research_result.output}")

# Inspect the complete message history
print(f"\n📋 Message History Analysis:")
messages = research_result.all_messages()

print_all_messages(messages)  # from utils.py
show_metrics(research_result.usage)  # from utils.py
