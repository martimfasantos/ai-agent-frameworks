import asyncio
import os

from ag2 import Agent, Middleware
from ag2.middleware import BaseMiddleware
from ag2.config import OpenAIConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2's Middleware with the following features:
- BaseMiddleware class for intercepting agent LLM calls
- on_llm_call hook to log, transform, or gate model requests
- on_turn hook to intercept full agent turns
- Composing multiple middlewares on a single agent

Middleware intercepts and modifies agent behavior without changing
agent code: log, filter, transform, retry, or gate interactions.
AG2 also ships builtins (CallTracerMiddleware, RetryMiddleware,
TokenLimiter, MetricsMiddleware) you can use instead of rolling
your own.

For more details, visit:
https://docs.ag2.ai/latest/docs/beta/middleware/
-------------------------------------------------------
"""


# --- 1. A tracing middleware that logs LLM calls ---
# Named CallTracer, not Logging, so it does not shadow the builtin
# ag2.middleware.LoggingMiddleware.
class CallTracerMiddleware(BaseMiddleware):
    """Logs every LLM call passing through the agent."""

    async def on_llm_call(self, call_next, events, context):
        print("  [CallTracerMiddleware] LLM call intercepted")
        response = await call_next(events, context)
        print("  [CallTracerMiddleware] LLM responded")
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
            Middleware(CallTracerMiddleware),
            Middleware(TimingMiddleware),
        ],
    )

    # --- Ask the agent a question ---
    print("=== Agent with Middleware Stack ===\n")
    reply = await agent.ask("What is the capital of France?")
    print(f"\nResponse: {reply.body}")


if __name__ == "__main__":
    asyncio.run(main())
