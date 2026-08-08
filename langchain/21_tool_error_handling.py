import os

from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    ToolCallRequest,
    ToolErrorMiddleware,
    ToolRetryMiddleware,
)
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore LangChain with the following features:
- ToolErrorMiddleware (new in langchain 1.3.14) turning tool exceptions into ToolMessage(status="error")
- The on_error handler receiving the exception plus the ToolCallRequest (tool name, args, call id)
- Composing ToolErrorMiddleware OUTSIDE ToolRetryMiddleware(on_failure="error")
- Why that composition order matters, measured by counting real tool attempts

An uncaught tool exception halts the whole agent run. ToolErrorMiddleware
converts the exceptions you opt into a ToolMessage the model can read and
recover from, while everything else still propagates. Because middleware is
composed first-is-outermost, the error middleware must sit OUTSIDE the retry
middleware: reversed, the inner error middleware swallows the exception before
the retry middleware ever sees one, so retries silently never happen.

For more details, visit:
https://docs.langchain.com/oss/python/langchain/middleware/built-in#tool-error
-------------------------------------------------------
"""


# --- 1. A tool that always fails, with an attempt counter as proof ---
attempts: list[str] = []


@tool
def fetch_exchange_rate(currency: str) -> str:
    """Fetch the current USD exchange rate for a currency code."""
    attempts.append(currency)
    raise ConnectionError(f"rate service unreachable (attempt {len(attempts)})")


# --- 2. The on_error handler: opt in per exception type ---
def on_tool_error(exc: Exception, request: ToolCallRequest) -> str | None:
    if isinstance(exc, ConnectionError):
        print(f"  [ToolErrorMiddleware] {request.tool_call['name']}"
              f"({request.tool_call['args']}) raised {type(exc).__name__}")
        return (
            f"`{request.tool_call['name']}` is unavailable ({type(exc).__name__}). "
            "Tell the user the rate could not be fetched and to try again later."
        )
    # Returning None re-raises: unhandled exceptions still halt the run.
    return None


# --- 3. The retry middleware: re-raise after exhausting retries ---
def make_retry() -> ToolRetryMiddleware:
    return ToolRetryMiddleware(
        max_retries=3,
        retry_on=(ConnectionError,),  # 1.3.14 narrows retries to retryable types
        on_failure="error",  # re-raise so ToolErrorMiddleware can handle it
        initial_delay=0.1,
        backoff_factor=0.0,  # constant delay, keeps the demo fast
        jitter=False,
    )


model = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=0)


def run(middleware: list[AgentMiddleware]) -> None:
    attempts.clear()
    agent = create_agent(
        model=model,
        tools=[fetch_exchange_rate],
        system_prompt="You are a currency assistant. Be concise, reply in one sentence.",
        middleware=middleware,
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What is the USD rate for EUR?"}]}
    )
    tool_messages = [m for m in result["messages"] if m.type == "tool"]
    print(f"  tool attempts actually made : {len(attempts)}")
    print(f"  ToolMessage status          : {[m.status for m in tool_messages]}")
    print(f"  final answer                : {result['messages'][-1].content}")
    print()


# --------------------------------------------------------------
# Example 1: correct order — error middleware OUTSIDE retry
# --------------------------------------------------------------
print("=== Example 1: [ToolErrorMiddleware, ToolRetryMiddleware] (correct) ===")
print("  request flows error -> retry -> tool, so the exception reaches retry first")
run([ToolErrorMiddleware(on_error=on_tool_error), make_retry()])

# --------------------------------------------------------------
# Example 2: reversed order — the retry middleware never fires
# --------------------------------------------------------------
print("=== Example 2: [ToolRetryMiddleware, ToolErrorMiddleware] (reversed) ===")
print("  retry is now outermost, so the inner error middleware swallows the")
print("  exception first and retry sees a successful call")
run([make_retry(), ToolErrorMiddleware(on_error=on_tool_error)])

# --- 4. Summary ---
print("=== Why the order matters ===")
print("  Middleware is composed first-is-outermost.")
print("  ToolErrorMiddleware must wrap ToolRetryMiddleware, otherwise retries are")
print("  silently skipped: 1 attempt instead of 4 (initial call + max_retries=3).")
