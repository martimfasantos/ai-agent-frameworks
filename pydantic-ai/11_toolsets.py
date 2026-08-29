import asyncio

from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.toolsets import (
    FunctionToolset,
    CombinedToolset,
    FilteredToolset,
    PrefixedToolset,
)
from pydantic_ai.tools import ToolDefinition

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- FunctionToolset for grouping related tools together
- PrefixedToolset to namespace tools with a prefix
- FilteredToolset to dynamically enable/disable tools per run
- CombinedToolset to merge multiple toolsets into one

Toolsets let you organize, namespace, filter, and compose collections
of tools independently of agents. This is powerful for building reusable
tool libraries, controlling which tools are available per context, and
avoiding name collisions when combining tools from different sources.

For more details, visit:
https://pydantic.dev/docs/ai/tools-toolsets/toolsets/
-----------------------------------------------------------------------
"""


# --- 1. Define tool functions ---
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The city name.
    """
    weather_data = {
        "london": "Cloudy, 14°C",
        "paris": "Sunny, 22°C",
        "tokyo": "Rainy, 18°C",
    }
    return weather_data.get(city.lower(), f"No data for {city}")


def get_population(city: str) -> str:
    """Get the population of a city.

    Args:
        city: The city name.
    """
    pop_data = {
        "london": "8.9 million",
        "paris": "2.1 million",
        "tokyo": "13.9 million",
    }
    return pop_data.get(city.lower(), f"No data for {city}")


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert between currencies (simulated).

    Args:
        amount: Amount to convert.
        from_currency: Source currency code (e.g. USD).
        to_currency: Target currency code (e.g. EUR).
    """
    rates = {"USD_EUR": 0.92, "EUR_USD": 1.09, "USD_GBP": 0.79, "GBP_USD": 1.27}
    key = f"{from_currency.upper()}_{to_currency.upper()}"
    rate = rates.get(key, 1.0)
    converted = amount * rate
    return f"{amount} {from_currency} = {converted:.2f} {to_currency}"


# --- 2. Create toolsets ---

# FunctionToolset groups related tools
city_toolset = FunctionToolset([get_weather, get_population])
finance_toolset = FunctionToolset([convert_currency])


async def main():

    # --------------------------------------------------------------
    # Example 1: Basic FunctionToolset
    # --------------------------------------------------------------
    print("=== Example 1: FunctionToolset ===")

    agent1 = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Answer questions about cities using the provided tools. Be concise.",
        toolsets=[city_toolset],
    )

    result1 = await agent1.run("What's the weather in Paris and its population?")
    print(f"Response: {result1.output}\n")

    # --------------------------------------------------------------
    # Example 2: PrefixedToolset (namespacing)
    # --------------------------------------------------------------
    print("=== Example 2: PrefixedToolset ===")

    # Prefix tool names to avoid collisions
    prefixed_city = PrefixedToolset(city_toolset, prefix="city")
    prefixed_finance = PrefixedToolset(finance_toolset, prefix="finance")

    # Combine prefixed toolsets into one
    combined = CombinedToolset([prefixed_city, prefixed_finance])

    agent2 = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Use the available tools to help the user. Be concise.",
        toolsets=[combined],
    )

    result2 = await agent2.run(
        "What's the weather in London and how much is 100 USD in EUR?"
    )
    print(f"Response: {result2.output}\n")

    # --------------------------------------------------------------
    # Example 3: FilteredToolset (dynamic filtering)
    # --------------------------------------------------------------
    print("=== Example 3: FilteredToolset ===")

    # Only allow weather-related tools (filter out population)
    def weather_only_filter(ctx: RunContext, tool_def: ToolDefinition) -> bool:
        """Only include tools with 'weather' in the name."""
        return "weather" in tool_def.name.lower()

    filtered = FilteredToolset(city_toolset, filter_func=weather_only_filter)

    agent3 = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Answer weather questions using available tools. Be concise.",
        toolsets=[filtered],
    )

    result3 = await agent3.run("Tell me about the weather in Tokyo.")
    print(f"Response: {result3.output}\n")

    # Show that the population tool was filtered out
    print("Filtered toolset only exposes weather tools, population tool is hidden.")


if __name__ == "__main__":
    asyncio.run(main())
