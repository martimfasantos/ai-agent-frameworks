import asyncio
import os

from autogen.beta import Agent
from autogen.beta.config import OpenAIConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2's Beta Agent with the following features:
- Tool functions on the beta Agent
- Event history showing tool call/result lifecycle

The beta Agent supports tools as plain functions passed via
the tools= parameter. The event history shows the full
tool-calling loop.

For more details, visit:
https://docs.ag2.ai/latest/docs/user-guide/release-roadmap/
-------------------------------------------------------
"""


def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    weather_data = {
        "lisbon": "Sunny, 25C",
        "london": "Cloudy, 15C",
        "tokyo": "Rainy, 18C",
    }
    return weather_data.get(city.lower(), f"No weather data for {city}")


def get_population(city: str) -> str:
    """Get the population of a city."""
    pop_data = {
        "lisbon": "~550,000",
        "london": "~9,000,000",
        "tokyo": "~14,000,000",
    }
    return pop_data.get(city.lower(), f"No population data for {city}")


async def main() -> None:
    agent = Agent(
        "city_assistant",
        (
            "You are a city information assistant. "
            "Use the provided tools to look up data. "
            "Reply in 2-3 sentences max."
        ),
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        tools=[get_weather, get_population],
    )

    print("=== Beta Agent: Tools ===\n")
    reply = await agent.ask("What's the weather and population of Lisbon?")
    print(f"Response: {reply.body}")

    print("\n=== Event History ===")
    for event in await reply.history.get_events():
        print(f"  {type(event).__name__}")


if __name__ == "__main__":
    asyncio.run(main())
