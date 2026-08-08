from strands import Agent, tool
from strands.hooks import (
    AfterInvocationEvent,
    AfterToolCallEvent,
    BeforeInvocationEvent,
    BeforeToolCallEvent,
    HookOrder,
)
from strands.models.openai import OpenAIModel

from settings import settings

"""
-------------------------------------------------------
In this example, we explore Strands Agents SDK with the following features:
- Lifecycle hooks for agent events
- BeforeInvocationEvent and AfterInvocationEvent hooks
- BeforeToolCallEvent and AfterToolCallEvent hooks
- Using agent.add_hook() to register event handlers
- Controlling execution priority with add_hook(..., order=) and HookOrder (v1.43.0)

Hooks let you intercept and react to events in the agent lifecycle — before
and after model invocations, and before and after each tool call. This is
useful for logging, metrics, guardrails, modifying tool inputs/outputs,
or cancelling tool calls based on custom logic. For authorization and
guardrails specifically, see the intervention API in 19_interventions.py.

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/agents/hooks/
-------------------------------------------------------
"""


# --- 1. Define a sample tool ---


@tool
def calculate(expression: str) -> str:
    """Evaluate a simple math expression.

    Args:
        expression: A math expression to evaluate (e.g., '2 + 3')
    """
    try:
        result = eval(expression)  # noqa: S307 — demo only, not for production
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


# --- 2. Define hook callback functions ---


def on_before_invocation(event: BeforeInvocationEvent):
    """Called before the agent starts processing."""
    msg_count = len(event.messages) if event.messages else 0
    print(f"[Hook] Before invocation — {msg_count} messages in context")


def on_after_invocation(event: AfterInvocationEvent):
    """Called after the agent finishes processing."""
    print(f"[Hook] After invocation — result available: {event.result is not None}")


def on_before_tool_call(event: BeforeToolCallEvent):
    """Called before each tool call. Can modify or cancel the call."""
    tool_name = event.tool_use.get("name", "unknown")
    print(f"[Hook] Before tool call — about to call: {tool_name}")
    # You can cancel a tool call: event.cancel_tool = True
    # Or change the tool: event.selected_tool = different_tool


def on_after_tool_call(event: AfterToolCallEvent):
    """Called after each tool call completes."""
    tool_name = event.tool_use.get("name", "unknown")
    had_error = event.exception is not None
    print(f"[Hook] After tool call — finished: {tool_name} (error={had_error})")
    # You can retry: event.retry = True


def on_before_tool_call_early(event: BeforeToolCallEvent):
    """Registered with order=HookOrder.SDK_FIRST, so it runs before the callback above."""
    print(f"[Hook order=SDK_FIRST] Runs first — {event.tool_use.get('name', 'unknown')}")


# --- 3. Configure model, create agent, and register hooks ---
openai_model = OpenAIModel(
    client_args={
        "api_key": settings.OPENAI_API_KEY.get_secret_value()
        if settings.OPENAI_API_KEY
        else ""
    },
    model_id=settings.OPENAI_MODEL_NAME,
)
# Default: Agent() uses Amazon Bedrock (requires AWS credentials)
agent = Agent(
    model=openai_model,
    tools=[calculate],
    callback_handler=None,
)

agent.add_hook(on_before_invocation)
agent.add_hook(on_after_invocation)
agent.add_hook(on_before_tool_call)
agent.add_hook(on_after_tool_call)

# Registered last, but order=SDK_FIRST puts it ahead of the callback above.
# Lower order runs first; same order preserves registration order.
agent.add_hook(on_before_tool_call_early, order=HookOrder.SDK_FIRST)

# --- 4. Run the agent to trigger hooks ---
print("=== Hooks: Lifecycle Event Callbacks ===\n")
result = agent("What is 42 * 17? Use the calculate tool.")

# --- 5. Print results ---
print(f"\nAgent response: {result.message}")

# --- 6. HookOrder constants ---
print("\nHookOrder constants (lower runs first):")
print(f"  SDK_FIRST={HookOrder.SDK_FIRST}  INTERVENTION_OUTPUT={HookOrder.INTERVENTION_OUTPUT}"
      f"  DEFAULT={HookOrder.DEFAULT}")
print(f"  INTERVENTION_INPUT={HookOrder.INTERVENTION_INPUT}  SDK_LAST={HookOrder.SDK_LAST}")
