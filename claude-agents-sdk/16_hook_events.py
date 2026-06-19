import asyncio

from dotenv import load_dotenv

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    HookEventMessage,
    HookMatcher,
    HookInput,
    HookJSONOutput,
    HookContext,
)

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Claude Agent SDK with the following features:
- Hook event streaming with include_hook_events=True
- Receiving HookEventMessage in the message stream
- Observing PreToolUse and PostToolUse lifecycle events
- Combining hook callbacks with event streaming for full observability

When include_hook_events is enabled, hook lifecycle events are emitted
as HookEventMessage objects in the message stream. This gives your
application visibility into every hook invocation — when it fired,
which tool triggered it, and what the hook decided — without needing
to rely solely on print statements inside hook callbacks.

For more details, visit:
https://platform.claude.com/docs/en/agent-sdk/hooks
-------------------------------------------------------
"""


# --- 1. Define a simple logging hook ---
async def log_hook(
    hook_input: HookInput,
    tool_use_id: str | None,
    context: HookContext,
) -> HookJSONOutput:
    """Allow all tools, just log them."""
    return {"continue_": True}


# --- 2. Configure with hook event streaming enabled ---
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob"],
    permission_mode="bypassPermissions",
    include_hook_events=True,
    hooks={
        "PreToolUse": [HookMatcher(matcher=None, hooks=[log_hook])],
        "PostToolUse": [HookMatcher(matcher=None, hooks=[log_hook])],
    },
)


# --- 3. Run and observe hook events in the stream ---
async def main():
    print("=== Hook Event Streaming ===\n")
    hook_event_count = 0

    async for message in query(
        prompt="List all Python files in the current directory using Glob.",
        options=options,
    ):
        if isinstance(message, HookEventMessage):
            hook_event_count += 1
            print(f"[HookEvent #{hook_event_count}]")
            print(f"  Event: {message.hook_event_name}")
            print(f"  Subtype: {message.subtype}")
            # Show key data fields without dumping the entire dict
            data = message.data
            if "tool_name" in data:
                print(f"  Tool: {data['tool_name']}")
            if "decision" in data:
                print(f"  Decision: {data['decision']}")
            print()

        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"--- Result ---")
            print(f"{message.result}")
            print(f"\nTotal hook events received: {hook_event_count}")


if __name__ == "__main__":
    asyncio.run(main())
