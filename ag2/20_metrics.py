import asyncio
import os

from prometheus_client import CollectorRegistry, generate_latest

from ag2 import Agent, tool
from ag2.config import OpenAIConfig
from ag2.middleware import MetricsMiddleware

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- MetricsMiddleware emitting Prometheus counters and histograms
- Sharing one middleware instance across several agents
- Scraping the registry the way Prometheus would

MetricsMiddleware is AG2 1.0's operational-telemetry surface, and
the natural replacement for the removed SQLite runtime logging. It
records agent turns, LLM calls, token usage, and tool executions
into a Prometheus CollectorRegistry. Production code exposes that
registry over HTTP with start_http_server(8000, registry=registry);
here we render the same exposition text in-process so the example
stays non-blocking.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/metrics.mdx
-------------------------------------------------------
"""

INTERESTING = (
    "ag2_agent_turns_total",
    "ag2_llm_calls_total",
    "ag2_llm_tokens_total",
    "ag2_tool_calls_total",
)


@tool
def convert_currency(amount: float, currency: str) -> str:
    """Convert an amount from EUR to another currency."""
    rates = {"usd": 1.09, "gbp": 0.84, "jpy": 171.0}
    rate = rates.get(currency.lower())
    if rate is None:
        raise ValueError(f"no rate for {currency}")
    return f"{amount} EUR = {amount * rate:.2f} {currency.upper()}"


async def main() -> None:
    # --- 1. One registry, one middleware, shared by every agent ---
    registry = CollectorRegistry()
    metrics = MetricsMiddleware(registry=registry)

    config = OpenAIConfig(model=settings.OPENAI_MODEL_NAME)

    assistant = Agent(
        "assistant",
        prompt="You are a helpful assistant. Answer in one sentence.",
        config=config,
        middleware=[metrics],
        tools=[convert_currency],
    )
    reviewer = Agent(
        "reviewer",
        prompt="You review answers. Reply 'Approved' or one sentence of feedback.",
        config=config,
        middleware=[metrics],
    )

    # --- 2. Generate some traffic, including a tool call and a tool error ---
    print("=== Generating traffic ===\n")
    reply = await assistant.ask("Convert 250 EUR to USD using the tool.")
    print(f"assistant: {reply.body}")

    failed = await assistant.ask("Now convert 250 EUR to Klingon darseks with the tool.")
    print(f"assistant: {failed.body}")

    review = await reviewer.ask(f"Review this answer: {reply.body}")
    print(f"reviewer:  {review.body}")

    # --- 3. Scrape the registry exactly as Prometheus would ---
    print("\n=== Prometheus exposition (filtered) ===\n")
    for line in generate_latest(registry).decode().splitlines():
        if line.startswith(INTERESTING):
            print(f"  {line}")


if __name__ == "__main__":
    asyncio.run(main())
