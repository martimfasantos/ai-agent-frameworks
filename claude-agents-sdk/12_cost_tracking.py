import asyncio

from dotenv import load_dotenv

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, ModelUsage

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Claude Agent SDK with the following features:
- Cost tracking via ResultMessage.total_cost_usd and usage dict
- Limiting agent turns with max_turns
- Setting a budget cap with max_budget_usd
- Controlling thinking depth with the effort parameter
- Per-model accounting via ResultMessage.model_usage (typed as ModelUsage)

These controls help manage agent costs in production. max_turns limits
how many tool-call rounds the agent can take, max_budget_usd sets a
hard dollar cap, and effort (low/medium/high/max) controls how deeply
the model reasons before responding.

For more details, visit:
https://platform.claude.com/docs/en/agent-sdk/cost-tracking
https://platform.claude.com/docs/en/agent-sdk/agent-loop
-------------------------------------------------------
"""

# --------------------------------------------------------------
# Example 1: Track Cost and Usage
# --------------------------------------------------------------
print("=== Example 1: Cost and Usage Tracking ===")


async def example_cost_tracking():
    async for message in query(
        prompt="Explain what a REST API is in two sentences.",
        options=ClaudeAgentOptions(),
    ):
        if isinstance(message, ResultMessage):
            print(f"Result: {message.result}")
            print(
                f"Cost: ${message.total_cost_usd:.6f}"
                if message.total_cost_usd
                else "Cost: N/A"
            )
            print(f"Turns: {message.num_turns}")
            print(
                f"Duration: {message.duration_ms}ms (API: {message.duration_api_ms}ms)"
            )
            if message.usage:
                print(f"Usage: {message.usage}")


asyncio.run(example_cost_tracking())

# --------------------------------------------------------------
# Example 2: Limit Turns
# --------------------------------------------------------------
print("\n=== Example 2: Limit Max Turns ===")


async def example_max_turns():
    options = ClaudeAgentOptions(
        max_turns=3,
        allowed_tools=["Read", "Glob"],
        permission_mode="bypassPermissions",
    )

    # When the agent runs out of turns, query() raises on the error result
    # after yielding the ResultMessage that carries the turn count
    try:
        async for message in query(
            prompt="Find and summarize all Python files in the current directory.",
            options=options,
        ):
            if isinstance(message, ResultMessage):
                print(f"Stopped after {message.num_turns} turns")
                print(f"Stop reason: {message.stop_reason}")
                print(f"Result: {message.result}")
    except Exception as error:
        print(f"Turn limit hit: {error}")


asyncio.run(example_max_turns())

# --------------------------------------------------------------
# Example 3: Budget Cap
# --------------------------------------------------------------
print("\n=== Example 3: Budget Cap ===")


async def example_budget_cap():
    options = ClaudeAgentOptions(
        max_budget_usd=0.05,  # 5 cents max
    )

    # Like max_turns, exceeding the cap surfaces as a raised error result --
    # whether it fires depends on how expensive the configured model is
    try:
        async for message in query(
            prompt="What is the capital of France?",
            options=options,
        ):
            if isinstance(message, ResultMessage):
                cost = message.total_cost_usd
                print(f"Result: {message.result}")
                print(f"Cost: ${cost:.6f}" if cost else "Cost: N/A")
                print(f"Budget limit: $0.05")
    except Exception as error:
        print(f"Budget cap hit: {error}")


asyncio.run(example_budget_cap())

# --------------------------------------------------------------
# Example 4: Effort Level
# --------------------------------------------------------------
print("\n=== Example 4: Effort Level ===")


async def example_effort():
    # Low effort for quick, simple answers
    options = ClaudeAgentOptions(effort="low")

    async for message in query(
        prompt="What is 2 + 2?",
        options=options,
    ):
        if isinstance(message, ResultMessage):
            print(f"[Low effort] Result: {message.result}")
            print(f"Duration: {message.duration_ms}ms")


asyncio.run(example_effort())

# --------------------------------------------------------------
# Example 5: Per-Model Usage (Whole-Tree Accounting)
# --------------------------------------------------------------
print("\n=== Example 5: Per-Model Usage ===")


async def example_model_usage():
    # A subagent run makes the difference visible: usage counts only the main
    # loop's tokens, while model_usage aggregates the whole agent tree
    options = ClaudeAgentOptions(
        allowed_tools=["Task"],
        permission_mode="bypassPermissions",
        max_turns=6,
    )

    async for message in query(
        prompt="Launch one general-purpose subagent to report today's date, then tell me what it said.",
        options=options,
    ):
        if isinstance(message, ResultMessage) and message.model_usage:
            for model, stats in message.model_usage.items():
                # stats is a ModelUsage TypedDict (root-exported since 0.2.126)
                usage: ModelUsage = stats
                print(f"Model: {model} ({usage.get('provider')})")
                print(f"  Input tokens:          {usage['inputTokens']}")
                print(f"  Output tokens:         {usage['outputTokens']}")
                print(f"  Cache read tokens:     {usage['cacheReadInputTokens']}")
                print(f"  Cache creation tokens: {usage['cacheCreationInputTokens']}")
                print(f"  Cost:                  ${usage['costUSD']:.6f}")
                print(f"  Context window:        {usage['contextWindow']}")

            # usage EXCLUDES subagent tokens, model_usage includes them
            main_loop_cache = (message.usage or {}).get("cache_creation_input_tokens")
            tree_cache = sum(
                m["cacheCreationInputTokens"] for m in message.model_usage.values()
            )
            print(f"\nCache creation tokens in usage (main loop only): {main_loop_cache}")
            print(f"Cache creation tokens in model_usage (whole tree): {tree_cache}")


asyncio.run(example_model_usage())
