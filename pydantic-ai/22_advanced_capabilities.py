import asyncio
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import (
    AbstractCapability,
    CombinedCapability,
    Hooks,
    PrepareTools,
)
from pydantic_ai.toolsets import FunctionToolset

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- CombinedCapability for bundling multiple capabilities together
- CapabilityOrdering for controlling capability evaluation order
- PrepareTools for dynamically filtering or modifying tools at runtime
- output_retries replacing deprecated retries parameter

These advanced capability patterns enable fine-grained control over
agent behavior composition. CombinedCapability bundles related
capabilities into reusable packages. CapabilityOrdering controls which
capability gets priority when multiple provide conflicting settings.
PrepareTools allows runtime tool filtering based on context.

For more details, visit:
https://ai.pydantic.dev/capabilities/
-----------------------------------------------------------------------
"""


# --- 1. Define toolsets for capabilities ---

math_toolset = FunctionToolset()


@math_toolset.tool_plain
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@math_toolset.tool_plain
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


text_toolset = FunctionToolset()


@text_toolset.tool_plain
def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


@text_toolset.tool_plain
def reverse_text(text: str) -> str:
    """Reverse a string."""
    return text[::-1]


# --- 2. Custom capabilities ---


@dataclass
class MathCapability(AbstractCapability[Any]):
    """Provides math tools."""

    def get_toolset(self):
        return math_toolset

    def get_instructions(self):
        return "Use math tools for calculations."


@dataclass
class TextCapability(AbstractCapability[Any]):
    """Provides text manipulation tools."""

    def get_toolset(self):
        return text_toolset

    def get_instructions(self):
        return "Use text tools for string operations."


async def main():

    # ------------------------------------------------------------------
    # Example 1: CombinedCapability -- bundle capabilities together
    # ------------------------------------------------------------------
    print("=== Example 1: CombinedCapability ===")

    combined = CombinedCapability(
        capabilities=[MathCapability(), TextCapability()],
    )

    agent1 = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Be concise.",
        capabilities=[combined],
    )

    result1 = await agent1.run("Add 15 and 27, then count the words in 'hello world foo'.")
    print(f"Response: {result1.output}\n")

    # ------------------------------------------------------------------
    # Example 2: CombinedCapability with Hooks -- ordering via chain
    # ------------------------------------------------------------------
    print("=== Example 2: CapabilityOrdering ===")

    hooks = Hooks()

    @hooks.on.before_model_request
    async def log_request(ctx: RunContext[None], request_context):
        print(f"  [Hook] Sending request (step {ctx.run_step})...")
        return request_context

    combined_ordered = CombinedCapability(
        capabilities=[MathCapability(), hooks],
    )

    agent2 = Agent(
        model=settings.OPENAI_MODEL_NAME,
        name="ordered_agent",
        instructions="Be concise. Use tools for calculations.",
        capabilities=[combined_ordered],
    )

    result2 = await agent2.run("What is 8 * 12?")
    print(f"Response: {result2.output}\n")

    # ------------------------------------------------------------------
    # Example 3: output_retries -- new retry parameter
    # ------------------------------------------------------------------
    print("=== Example 3: output_retries (replaces deprecated retries) ===")

    agent3 = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Be concise. Reply in one sentence.",
        output_retries=3,  # New parameter replacing deprecated 'retries'
    )

    result3 = await agent3.run("What is the speed of light?")
    print(f"Response: {result3.output}\n")

    # ------------------------------------------------------------------
    # Example 4: PrepareTools -- dynamic tool filtering
    # ------------------------------------------------------------------
    print("=== Example 4: PrepareTools Capability ===")

    async def only_math_tools(ctx, tool_defs):
        """Filter to only math-related tools at runtime."""
        return [td for td in tool_defs if td.name in ("add", "multiply")]

    agent4 = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Be concise. Use available tools.",
        capabilities=[
            MathCapability(),
            TextCapability(),
            PrepareTools(only_math_tools),
        ],
    )

    result4 = await agent4.run("Add 100 and 200.")
    print(f"Response: {result4.output}")
    print("(Only math tools were available despite TextCapability being registered)")


if __name__ == "__main__":
    asyncio.run(main())
