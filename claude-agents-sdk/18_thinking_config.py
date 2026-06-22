import asyncio

from dotenv import load_dotenv

from claude_agent_sdk import (
    query,
    ResultMessage,
    ClaudeAgentOptions,
    ThinkingConfig,
    ThinkingConfigEnabled,
    ThinkingConfigAdaptive,
    ThinkingConfigDisabled,
)

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Claude Agent SDK with the following features:
- ThinkingConfig for controlling extended thinking behavior
- ThinkingConfigEnabled: always show thinking with token budget
- ThinkingConfigAdaptive: let the model decide when to think
- ThinkingConfigDisabled: suppress thinking entirely
- max_thinking_tokens to set thinking budget

Extended thinking (new in SDK 0.2.x) lets you control whether
Claude shows its reasoning process. Enabled mode forces visible
chain-of-thought, adaptive lets Claude decide based on complexity,
and disabled suppresses it for faster, cheaper responses.

For more details, visit:
https://platform.claude.com/docs/en/agent-sdk/configuration
-------------------------------------------------------
"""


async def main():
    # ------------------------------------------------------------------
    # Example 1: Adaptive thinking (model decides when to think)
    # ------------------------------------------------------------------
    print("=== Example 1: Adaptive Thinking ===")

    async for message in query(
        prompt="What is 2 + 2?",
        options=ClaudeAgentOptions(
            thinking=ThinkingConfigAdaptive(type="adaptive"),
            max_turns=1,
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"Response: {message.result[:200]}")
    print()

    # ------------------------------------------------------------------
    # Example 2: Thinking enabled with token budget
    # Forces Claude to show its reasoning process.
    # ------------------------------------------------------------------
    print("=== Example 2: Thinking Enabled (budget: 2000 tokens) ===")

    async for message in query(
        prompt="Explain the halting problem in simple terms.",
        options=ClaudeAgentOptions(
            thinking=ThinkingConfigEnabled(type="enabled", budget_tokens=2000),
            max_turns=1,
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"Response: {message.result[:300]}")
    print()

    # ------------------------------------------------------------------
    # Example 3: Thinking disabled (faster, no reasoning shown)
    # ------------------------------------------------------------------
    print("=== Example 3: Thinking Disabled ===")

    async for message in query(
        prompt="Name 3 prime numbers.",
        options=ClaudeAgentOptions(
            thinking=ThinkingConfigDisabled(type="disabled"),
            max_turns=1,
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"Response: {message.result[:200]}")


if __name__ == "__main__":
    asyncio.run(main())
