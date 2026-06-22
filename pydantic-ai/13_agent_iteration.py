import asyncio

from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRun

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Agent iteration with agent.iter() for node-by-node control
- Inspecting each step of the agent's execution
- Accessing intermediate state via AgentRun
- Fine-grained control over the agent execution loop

Agent iteration gives you step-by-step control over the agent's internal
execution loop. Instead of running the agent to completion, you can inspect
each node (user prompt handling, model requests, tool calls) as it executes,
enabling logging, debugging, or custom control flow between steps.

For more details, visit:
https://ai.pydantic.dev/agents/#agent-level-iteration
-----------------------------------------------------------------------
"""

# --- 1. Create a simple agent with a tool ---
agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions="You are a helpful assistant. Use tools when available.",
)


@agent.tool_plain
def get_temperature(city: str) -> str:
    """Get the current temperature for a city.

    Args:
        city: The name of the city.
    """
    temps = {"london": "14°C", "paris": "22°C", "tokyo": "18°C", "lisbon": "26°C"}
    return temps.get(city.lower(), f"No data for {city}")


# --- 2. Run with iteration ---
async def main():

    # --------------------------------------------------------------
    # Example 1: Basic iteration — inspect each node
    # --------------------------------------------------------------
    print("=== Example 1: Step-by-Step Iteration ===\n")

    step_count = 0
    async with agent.iter("What's the temperature in Lisbon?") as run:
        run: AgentRun
        async for node in run:
            step_count += 1
            node_type = type(node).__name__
            print(f"  Step {step_count}: {node_type}")

    # After iteration completes, get the final result
    result = run.result
    print(f"\nFinal output: {result.output}")
    print(f"Total steps: {step_count}")
    print()

    # --------------------------------------------------------------
    # Example 2: Access messages during iteration
    # --------------------------------------------------------------
    print("=== Example 2: Inspect Messages During Iteration ===\n")

    async with agent.iter("What is the temperature in Paris and Tokyo?") as run:
        async for node in run:
            node_type = type(node).__name__
            # Check current messages after each step
            current_messages = run.all_messages()
            print(f"  Node: {node_type} | Messages so far: {len(current_messages)}")

    result = run.result
    print(f"\nFinal output: {result.output}")
    print(f"Total messages: {len(run.all_messages())}")
    print()

    # --------------------------------------------------------------
    # Example 3: Usage tracking during iteration
    # --------------------------------------------------------------
    print("=== Example 3: Usage Tracking During Iteration ===\n")

    async with agent.iter("Compare temperatures in London and Lisbon.") as run:
        async for node in run:
            usage = run.usage
            print(
                f"  {type(node).__name__}: "
                f"requests={usage.requests}, "
                f"tool_calls={usage.tool_calls}, "
                f"tokens={usage.total_tokens}"
            )

    result = run.result
    final_usage = run.usage
    print(f"\nFinal output: {result.output}")
    print(
        f"Final usage: {final_usage.requests} requests, {final_usage.tool_calls} tool calls"
    )


if __name__ == "__main__":
    asyncio.run(main())
