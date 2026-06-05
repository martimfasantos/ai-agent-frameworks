import asyncio
import os

from autogen.beta import Agent, MemoryStream
from autogen.beta.config import OpenAIConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2's Beta MemoryStream with the following features:
- MemoryStream for persistent agent conversation memory
- Sharing a stream between multiple agent interactions
- Inspecting stream events to see conversation history

AG2 v0.13 introduces MemoryStream, a structured event log that
agents use for conversation history. Unlike raw message lists,
MemoryStream supports compaction, filtering, and sharing across
agent turns, enabling long-running agent sessions without context
window overflow.

For more details, visit:
https://docs.ag2.ai/latest/docs/user-guide/beta/memory
-------------------------------------------------------
"""


async def main() -> None:
    # --- Create a shared memory stream ---
    stream = MemoryStream()

    # --- Create agent with the stream ---
    agent = Agent(
        name="assistant",
        prompt="You are a helpful assistant. Be concise. Remember context from earlier.",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
    )

    # --- First interaction ---
    print("=== Turn 1: Introduce context ===")
    reply1 = await agent.ask(
        "My name is Alice and I work at Acme Corp.",
        stream=stream,
    )
    print(f"Response: {reply1.body}\n")

    # --- Second interaction (agent should remember) ---
    print("=== Turn 2: Test memory ===")
    reply2 = await agent.ask(
        "What is my name and where do I work?",
        stream=stream,
    )
    print(f"Response: {reply2.body}\n")

    # --- Inspect the stream history ---
    print("=== Memory Stream Contents ===")
    events = await stream.history.get_events()
    print(f"Total events in stream: {len(events)}")
    for i, event in enumerate(events):
        event_type = type(event).__name__
        preview = str(event)[:80]
        print(f"  [{i}] {event_type}: {preview}...")


if __name__ == "__main__":
    asyncio.run(main())
