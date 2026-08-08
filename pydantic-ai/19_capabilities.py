import asyncio
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import AbstractCapability, Hooks, Thinking
from pydantic_ai.toolsets import FunctionToolset

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Capabilities as composable units of agent behavior
- Built-in capabilities (Thinking, Hooks)
- Custom capabilities with tools and instructions
- Composing multiple capabilities on a single agent

Capabilities bundle related behavior (tools, hooks, instructions,
model settings) into reusable units. Instead of threading many arguments
through the Agent constructor, you package behavior into a capability
and pass it via the `capabilities` parameter. This makes agent
configuration modular and reusable across projects.

For more details, visit:
https://pydantic.dev/docs/ai/capabilities/overview/
-----------------------------------------------------------------------
"""


# --- 1. Define a custom capability ---
# A capability that provides math tools and instructions


math_toolset = FunctionToolset()


@math_toolset.tool_plain
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@math_toolset.tool_plain
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@dataclass
class MathTools(AbstractCapability[Any]):
    """Provides basic math operations as tools plus math-specific instructions."""

    def get_toolset(self):
        return math_toolset

    def get_instructions(self):
        return "When performing calculations, always use the provided math tools rather than computing in your head. Show the tool result."


# --- 2. Define a hooks-based capability for logging ---

hooks = Hooks()


@hooks.on.before_model_request
async def log_request(ctx: RunContext, request_context):
    agent_name = ctx.agent.name if ctx.agent else "unknown"
    print(f"  [Hook] Agent '{agent_name}' sending request...")
    return request_context


@hooks.on.after_model_request
async def log_response(ctx: RunContext, *, request_context, response):
    print(f"  [Hook] Response received")
    return response


async def main():

    # --------------------------------------------------------------
    # Example 1: Built-in Thinking capability
    # --------------------------------------------------------------
    print("=== Example 1: Built-in Thinking Capability ===")

    agent1 = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Be concise. Reply in one sentence.",
        capabilities=[Thinking(effort="low")],
    )

    result1 = await agent1.run("What is 7 * 13?")
    print(f"Response: {result1.output}\n")

    # --------------------------------------------------------------
    # Example 2: Custom capability with tools
    # --------------------------------------------------------------
    print("=== Example 2: Custom MathTools Capability ===")

    agent2 = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Be concise. Use the math tools provided.",
        capabilities=[MathTools()],
    )

    result2 = await agent2.run("What is 42 + 58, and what is 7 * 9?")
    print(f"Response: {result2.output}\n")

    # --------------------------------------------------------------
    # Example 3: Composing multiple capabilities
    # --------------------------------------------------------------
    print("=== Example 3: Composing Multiple Capabilities ===")

    agent3 = Agent(
        model=settings.OPENAI_MODEL_NAME,
        name="math_agent",
        instructions="Be concise. Use the math tools for calculations.",
        capabilities=[
            MathTools(),  # provides math tools + instructions
            hooks,  # provides request/response logging
        ],
    )

    result3 = await agent3.run("What is 15 * 4?")
    print(f"Response: {result3.output}\n")

    # Show that the hooks fired by checking the printed log lines above
    print(
        "The [Hook] log lines above prove the Hooks capability intercepted the lifecycle."
    )


if __name__ == "__main__":
    asyncio.run(main())
