import asyncio
import os

from ag2 import Agent, tool
from ag2.config import OpenAIConfig
from ag2.events import ToolCallEvent, ToolResultEvent

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- Declaring tools with the @tool decorator
- Passing them to an Agent via tools=
- Reading the tool-call lifecycle out of the reply history

Tools let an agent call Python functions to fetch data or take
actions. AG2 runs the whole loop: the model picks a tool, AG2
executes it, feeds the result back, and the model answers. The
docstring of each function becomes the schema the model sees.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/tools/tools.mdx
-------------------------------------------------------
"""


# --- 1. Define custom tools ---
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    weather_data = {
        "lisbon": "Sunny, 25°C",
        "london": "Cloudy, 15°C",
        "tokyo": "Rainy, 18°C",
    }
    return weather_data.get(city.lower(), f"No weather data for {city}")


@tool
def get_population(city: str) -> str:
    """Get the population of a city."""
    pop_data = {
        "lisbon": "~550,000",
        "london": "~9,000,000",
        "tokyo": "~14,000,000",
    }
    return pop_data.get(city.lower(), f"No population data for {city}")


async def main() -> None:
    # --- 2. Create an agent with tools ---
    assistant = Agent(
        "city_assistant",
        prompt=(
            "You are a city information assistant. "
            "Use the tools to look up data, then give a brief summary. "
            "Reply in 2-3 sentences max."
        ),
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        tools=[get_weather, get_population],
    )

    # --- 3. Ask a question that needs both tools ---
    print("=== Agent with tools ===\n")
    reply = await assistant.ask("What's the weather and population of Lisbon?")
    print(f"Response: {reply.body}")

    # --- 4. Prove the tools actually fired ---
    print("\n=== Tool activity ===")
    for event in await reply.context.stream.history.get_events():
        if isinstance(event, ToolCallEvent):
            print(f"  -> called {event.name}({event.arguments})")
        elif isinstance(event, ToolResultEvent):
            text = " ".join(str(part.content) for part in event.result.parts)
            print(f"  <- {event.name} returned {text!r}")


if __name__ == "__main__":
    asyncio.run(main())
