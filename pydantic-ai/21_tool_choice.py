import asyncio

from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.settings import ToolOrOutput

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- tool_choice model setting to control tool calling behavior
- 'auto' (default): model decides whether to call tools
- 'none': model cannot call any tools
- ToolOrOutput: restrict the model to a subset of function tools while
  still letting the agent finish with a final output

The tool_choice setting gives you fine-grained control over how the
model interacts with available tools. Note: the bare 'required' value
and a plain list[str] of tool names force a tool call on every step,
so they are only valid when an output tool exists (e.g. via per-step
variation from a capability); for text-output agents, use ToolOrOutput
so the agent can still produce a final answer.

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
    # ------------------------------------------------------------------
    print("=== Example 1: tool_choice='auto' (default) ===")

    result1 = await agent.run(
        "What's the weather in Paris?",
        model_settings={"tool_choice": "auto"},
    )
    print(f"Response: {result1.output}")
    print(f"Usage: {result1.usage.input_tokens} input tokens\n")

    # ------------------------------------------------------------------
    # Example 2: ToolOrOutput -- restrict to a named tool, keep output
    # ------------------------------------------------------------------
    print("=== Example 2: ToolOrOutput(['get_weather']) ===")

    result2 = await agent.run(
        "Tell me about Tokyo's weather and population.",
        model_settings={"tool_choice": ToolOrOutput(["get_weather"])},
    )
    print(f"Response: {result2.output}")
    print(f"(Only get_weather was offered; get_population was withheld)")
    print(f"Usage: {result2.usage.input_tokens} input tokens\n")

    # ------------------------------------------------------------------
    # Example 3: tool_choice='none' -- disable tools
    # ------------------------------------------------------------------
    print("=== Example 3: tool_choice='none' ===")

    result3 = await agent.run(
        "What's the weather in London?",
        model_settings={"tool_choice": "none"},
    )
    print(f"Response: {result3.output}")
    print(f"(Model answered from training data, no tools called)\n")

    # ------------------------------------------------------------------
    # Example 4: ToolOrOutput on a single compute tool
    # ------------------------------------------------------------------
    print("=== Example 4: ToolOrOutput(['calculate']) ===")

    # ToolOrOutput keeps output available, so the agent can call the
    # tool and then answer in natural language without looping forever.
    forced_agent = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Use the calculate tool for math, then state the result.",
    )

    @forced_agent.tool_plain
    def calculate(expression: str) -> str:
        """Evaluate a math expression."""
        try:
            return str(eval(expression))
        except Exception:
            return "Error evaluating expression"

    result4 = await forced_agent.run(
        "What is 42 * 7?",
        model_settings={"tool_choice": ToolOrOutput(["calculate"])},
    )
    print(f"Response: {result4.output}")


if __name__ == "__main__":
    asyncio.run(main())
