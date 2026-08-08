import asyncio

from dotenv import load_dotenv

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    ResultMessage,
    StreamEvent,
)

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Claude Agent SDK with the following features:
- Cancelling an in-flight turn with await client.interrupt()
- Reading ResultMessage.terminal_reason to tell why a turn ended
- Draining receive_response() after an interrupt before the next query()
- Observing terminal_reason="max_turns" when the turn limit is hit

interrupt() is the only way to stop a turn that is already running, and
terminal_reason (SDK 0.2.126) is what makes the outcome observable:
"completed" vs "aborted_streaming"/"aborted_tools" vs "max_turns".
The interrupted turn still emits its own ResultMessage, so you must
finish iterating receive_response() before sending the next prompt --
otherwise the next turn reads the dead turn's buffered messages.

For more details, visit:
https://code.claude.com/docs/en/agent-sdk/python
-------------------------------------------------------
"""

# --------------------------------------------------------------
# Example 1: Interrupt a Running Turn
# --------------------------------------------------------------
print("=== Example 1: Interrupt a Running Turn ===")


async def example_interrupt():
    # include_partial_messages gives us text deltas, so we can interrupt
    # as soon as the model starts speaking instead of guessing at a delay
    options = ClaudeAgentOptions(include_partial_messages=True)

    async with ClaudeSDKClient(options) as client:
        # --- 1. Start a deliberately long turn ---
        await client.query(
            "Count from 1 to 300. Print one number per line with a short note on each."
        )

        # --- 2. Interrupt on the first text delta, then keep draining ---
        interrupted = False
        deltas_after_interrupt = 0

        async for message in client.receive_response():
            if isinstance(message, StreamEvent):
                delta = message.event.get("delta", {})
                if delta.get("type") == "text_delta":
                    if not interrupted:
                        await client.interrupt()
                        interrupted = True
                        print("  [interrupt() sent while the model was streaming]")
                    else:
                        deltas_after_interrupt += 1

            # The aborted turn still produces a ResultMessage -- reaching it
            # is what drains the buffer and makes the client reusable
            if isinstance(message, ResultMessage):
                print(f"  subtype:         {message.subtype}")
                print(f"  terminal_reason: {message.terminal_reason}")
                print(f"  is_error:        {message.is_error}")
                print(f"  result:          {message.result}")
                print(f"  extra deltas after interrupt: {deltas_after_interrupt}")

        # --- 3. Same client, next turn: the buffer is clean ---
        print("\n  Sending a follow-up turn on the same client...")
        await client.query("What is 2 + 2? Reply with just the number.")

        async for message in client.receive_response():
            if isinstance(message, ResultMessage):
                print(f"  terminal_reason: {message.terminal_reason}")
                print(f"  result:          {message.result}")


asyncio.run(example_interrupt())

# --------------------------------------------------------------
# Example 2: terminal_reason When the Turn Limit Is Hit
# --------------------------------------------------------------
print("\n=== Example 2: terminal_reason=max_turns ===")


async def example_max_turns():
    options = ClaudeAgentOptions(
        max_turns=1,
        allowed_tools=["Glob", "Read"],
        permission_mode="bypassPermissions",
    )

    # ClaudeSDKClient yields error results as ResultMessage; query() raises on
    # them instead, so the client is what lets us read terminal_reason here
    async with ClaudeSDKClient(options) as client:
        await client.query(
            "List every .py file here with Glob, then read three of them and summarise each."
        )

        async for message in client.receive_response():
            if isinstance(message, ResultMessage):
                print(f"  subtype:         {message.subtype}")
                print(f"  terminal_reason: {message.terminal_reason}")
                print(f"  stop_reason:     {message.stop_reason}")
                print(f"  turns used:      {message.num_turns}")


asyncio.run(example_max_turns())

print("\n=== terminal_reason values ===")
print("completed:         the turn finished on its own")
print("max_turns:         max_turns was reached")
print("api_error:         the upstream API call failed")
print("aborted_streaming: interrupted while the model was generating text")
print("aborted_tools:     interrupted while a tool call was in flight")
print("None:              older CLI, or a result that bypassed the query loop")
