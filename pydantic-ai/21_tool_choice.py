import asyncio

from dotenv import load_dotenv

from pydantic_ai import Agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- tool_choice model setting to control tool calling behavior
- 'auto' (default): model decides whether to call tools
- 'none': model cannot call any tools
- Per-run tool_choice override via model_settings

The tool_choice setting gives you fine-grained control over how the
model interacts with available tools. This is useful for disabling
tools temporarily without removing them from the agent.

Note: As of v1.104.0, tool_choice='required' is no longer compatible
with agent.run() because it prevents the agent from producing a final
text response. For forced tool calls, use pydantic_ai.direct instead.

For more details, visit:
https://ai.pydantic.dev/agents/#model-settings
-----------------------------------------------------------------------
"""


# --- 1. Define a simple agent with tools ---
agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions="Be concise. Use tools when available.",
)


@agent.tool_plain
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    weather_data = {
        "London": "cloudy, 14C",
        "Paris": "sunny, 22C",
        "Tokyo": "rainy, 18C",
    }
    return weather_data.get(city, f"No data for {city}")


@agent.tool_plain
def get_population(city: str) -> str:
    """Get the population of a city."""
    pop_data = {
        "London": "8.8 million",
        "Paris": "2.1 million",
        "Tokyo": "13.9 million",
    }
    return pop_data.get(city, f"No data for {city}")


async def main():

    # ------------------------------------------------------------------
    # Example 1: tool_choice='auto' (default behavior)
    # The model decides on its own whether to call a tool.
    # ------------------------------------------------------------------
    print("=== Example 1: tool_choice='auto' (default) ===")

    result1 = await agent.run(
        "What's the weather in Paris?",
        model_settings={"tool_choice": "auto"},
    )
    print(f"Response: {result1.output}")
    print(f"Usage: {result1.usage().input_tokens} input tokens\n")

    # ------------------------------------------------------------------
    # Example 2: tool_choice='none' -- disable tools entirely
    # The model answers from its own knowledge, ignoring tools.
    # ------------------------------------------------------------------
    print("=== Example 2: tool_choice='none' ===")

    result2 = await agent.run(
        "What's the weather in London?",
        model_settings={"tool_choice": "none"},
    )
    print(f"Response: {result2.output}")
    print(f"(Model answered from training data, no tools called)\n")

    # ------------------------------------------------------------------
    # Example 3: Switching tool_choice per-run
    # Same agent, different behavior per call.
    # ------------------------------------------------------------------
    print("=== Example 3: Per-run switching ===")

    # First call: tools enabled
    r_auto = await agent.run(
        "Population of Tokyo?",
        model_settings={"tool_choice": "auto"},
    )
    print(f"With tools (auto): {r_auto.output}")

    # Second call: tools disabled
    r_none = await agent.run(
        "Population of Tokyo?",
        model_settings={"tool_choice": "none"},
    )
    print(f"Without tools (none): {r_none.output}")


if __name__ == "__main__":
    asyncio.run(main())
