import asyncio
import os

from autogen.beta import Agent, Middleware
from autogen.beta.middleware import BaseMiddleware
from autogen.beta.config import OpenAIConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2's Beta Middleware with the following features:
- BaseMiddleware class for intercepting agent LLM calls
- on_llm_call hook to log, transform, or gate model requests
- on_turn hook to intercept full agent turns
- Composing multiple middlewares on a single agent

AG2 v0.13 introduces Middleware, a powerful mechanism to intercept
and modify agent behavior without changing agent code. Middlewares
can log, filter, transform, retry, or gate agent interactions.

For more details, visit:
https://docs.ag2.ai/latest/docs/user-guide/beta/middleware
-------------------------------------------------------
"""


# --- 1. A logging middleware that tracks LLM calls ---
class LoggingMiddleware(BaseMiddleware):
    """Logs every LLM call passing through the agent."""

    async def on_llm_call(self, call_next, events, context):
        print("  [LoggingMiddleware] LLM call intercepted")
        response = await call_next(events, context)
        print("  [LoggingMiddleware] LLM responded")
        return response


# --- 2. A timing middleware that measures latency ---
class TimingMiddleware(BaseMiddleware):
    """Measures how long each turn takes."""

    async def on_turn(self, call_next, event, context):
        import time
        start = time.perf_counter()
        response = await call_next(event, context)
        elapsed = time.perf_counter() - start
        print(f"  [TimingMiddleware] Turn completed in {elapsed:.2f}s")
        return response


async def main() -> None:
    # --- Create agent with middleware stack ---
    agent = Agent(
        name="assistant",
        prompt="You are a helpful assistant. Be concise (1-2 sentences max).",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        middleware=[
            Middleware(LoggingMiddleware),
            Middleware(TimingMiddleware),
        ],
    )

    # --- Ask the agent a question ---
    print("=== Agent with Middleware Stack ===\n")
    reply = await agent.ask("What is the capital of France?")
    print(f"\nResponse: {reply.body}")


if __name__ == "__main__":
    asyncio.run(main())
