import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from pydantic_ai import Agent, UsageLimits
from pydantic_ai.exceptions import UsageLimitExceeded

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- RunUsage.cost: best-effort cost of a run in USD, computed for you
- UsageLimits(cost_limit=...) to cap spend instead of guessing at tokens
- per_request_input_tokens_limit to reject a single oversized request
- Summing RunUsage across runs to get a combined token/cost total

Before v2.23 the only way to know what a run cost was to multiply token
counts by prices you hard-coded yourself. `cost` is now a first-class
field on every usage object, and `cost_limit` turns it into a budget
guard: the run is aborted with UsageLimitExceeded as soon as the spend
would pass the limit, so a runaway agent cannot quietly burn money.

For more details, visit:
https://pydantic.dev/docs/ai/api/pydantic-ai/usage/
-----------------------------------------------------------------------
"""

agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions="Be concise. Reply in one short sentence.",
)


async def main():

    # ------------------------------------------------------------------
    # Example 1: Read the real USD cost of a run
    # ------------------------------------------------------------------
    print("=== Example 1: RunUsage.cost ===")

    result = await agent.run("Name the highest mountain in Europe.")
    usage = result.usage

    print(f"Response: {result.output}")
    print(f"Input tokens:  {usage.input_tokens}")
    print(f"Output tokens: {usage.output_tokens}")
    # `cost` is a Decimal in USD, or None when the model/provider cannot be priced
    print(f"Cost (USD):    {usage.cost:.8f}" if usage.cost else "Cost: unavailable")
    print()

    # ------------------------------------------------------------------
    # Example 2: cost_limit as a spend guard
    # ------------------------------------------------------------------
    print("=== Example 2: UsageLimits(cost_limit=...) ===")

    # A deliberately tiny budget: one hundredth of a cent
    tiny_budget = Decimal("0.0000001")
    try:
        await agent.run(
            "Write a detailed history of the Portuguese maritime discoveries.",
            usage_limits=UsageLimits(cost_limit=tiny_budget),
        )
    except UsageLimitExceeded as exc:
        print(f"Budget of ${tiny_budget} USD enforced -> UsageLimitExceeded")
        print(f"  {exc}")
    print()

    # ------------------------------------------------------------------
    # Example 3: per_request_input_tokens_limit vs. input_tokens_limit
    # ------------------------------------------------------------------
    print("=== Example 3: per_request_input_tokens_limit ===")

    # input_tokens_limit is cumulative over the whole run; this one caps the
    # size of any single request, guarding against an oversized context.
    long_prompt = "Summarise this: " + ("Pydantic AI is a Python agent framework. " * 200)

    try:
        await agent.run(
            long_prompt,
            usage_limits=UsageLimits(per_request_input_tokens_limit=100),
        )
    except UsageLimitExceeded as exc:
        print("A single request exceeding 100 input tokens was rejected")
        print(f"  {exc}")
    print()

    # ------------------------------------------------------------------
    # Example 4: Summing usage across several runs
    # ------------------------------------------------------------------
    print("=== Example 4: Aggregating RunUsage across runs ===")

    # RunUsage supports `+`, so tracking the spend of a whole session is a sum.
    first = await agent.run("What is the capital of Japan?")
    second = await agent.run("What is the capital of Peru?")
    combined = first.usage + second.usage

    for label, run in (("First run ", first), ("Second run", second)):
        print(
            f"{label}: input={run.usage.input_tokens:>4}  "
            f"output={run.usage.output_tokens:>3}  "
            f"cost=${run.usage.cost:.8f}"
        )

    print(
        f"Combined  : input={combined.input_tokens:>4}  "
        f"output={combined.output_tokens:>3}  "
        f"cost=${combined.cost:.8f}"
    )
    # cache_hit_ratio is the share of input tokens the provider served from its
    # prompt cache -- 0% here because these prompts are far below the cache
    # threshold (OpenAI only caches prefixes of 1024+ tokens).
    print(f"Cache hit ratio across both runs: {combined.cache_hit_ratio:.2%}")


if __name__ == "__main__":
    asyncio.run(main())
