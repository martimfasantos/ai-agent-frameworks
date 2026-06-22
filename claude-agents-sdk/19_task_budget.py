import asyncio

from dotenv import load_dotenv

from claude_agent_sdk import (
    query,
    ResultMessage,
    ClaudeAgentOptions,
    TaskBudget,
)

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Claude Agent SDK with the following features:
- TaskBudget for controlling agent resource consumption
- max_budget_usd to set a dollar cap on API spend per task
- TaskBudget for a total token budget the model paces itself against
- Combining budget controls for predictable agent costs

Task budgets (SDK 0.2.x) let you cap how much an agent
can spend on a single task. This is critical for production
deployments where runaway agents could generate unexpected costs.
max_budget_usd sets a dollar cap, while TaskBudget(total=...) gives
the model a total token budget it is made aware of so it can pace
tool use and wrap up before the limit.

For more details, visit:
https://platform.claude.com/docs/en/agent-sdk/configuration
-------------------------------------------------------
"""


async def main():
    # ------------------------------------------------------------------
    # Example 1: Simple dollar budget cap
    # ------------------------------------------------------------------
    print("=== Example 1: Dollar Budget Cap ===")

    async for message in query(
        prompt="Write a haiku about programming.",
        options=ClaudeAgentOptions(
            max_budget_usd=1.00,  # Cap total spend at $1.00
            max_turns=1,
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"Response: {message.result}")
    print()

    # ------------------------------------------------------------------
    # Example 2: TaskBudget with a total token budget
    # ------------------------------------------------------------------
    print("=== Example 2: TaskBudget with Token Limit ===")

    async for message in query(
        prompt="Research and summarize the history of Python.",
        options=ClaudeAgentOptions(
            task_budget=TaskBudget(
                total=25000,  # Total token budget (model minimum is 20,000)
            ),
            max_turns=3,
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"Response: {message.result[:300]}")
        elif isinstance(message, ResultMessage) and message.subtype == "budget_exceeded":
            print("Budget exceeded - agent stopped early")

    print("\n=== Budget Controls Summary ===")
    print("max_budget_usd:    Hard dollar cap on total API spend")
    print("TaskBudget(total): Total token budget the model paces against")
    print("max_turns:         Maximum agent reasoning iterations")


if __name__ == "__main__":
    asyncio.run(main())
