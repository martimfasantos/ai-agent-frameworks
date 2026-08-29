import asyncio
import json
import os
from collections import Counter

from ag2 import Agent, MemoryStream, tool
from ag2.config import OpenAIConfig
from ag2.events import BaseEvent, ToolCallEvent, UsageEvent

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- MemoryStream.subscribe() to capture every event as it happens
- stream.where(...) to subscribe to one event type only
- Persisting the event log to disk for post-hoc analysis

AG2 1.0 removed autogen.runtime_logging and its SQLite schema.
Observability is now stream-based: every agent action lands on the
stream as a typed event, and subscribers decide what to record.
Here we mirror the old workflow — capture a session, write it to a
file, then query it afterwards for event counts and token usage.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/advanced/stream.mdx
-------------------------------------------------------
"""

LOG_PATH = "res/ag2_event_log.jsonl"


@tool
def get_distance(city_a: str, city_b: str) -> str:
    """Get the great-circle distance between two cities."""
    return f"{city_a} to {city_b}: 2,780 km"


async def main() -> None:
    os.makedirs("res", exist_ok=True)

    # --- 1. Create a stream and subscribe to everything on it ---
    stream = MemoryStream()
    log: list[BaseEvent] = []

    @stream.subscribe()
    async def record(event: BaseEvent) -> None:
        log.append(event)

    # --- 2. Subscribe to one event type only, for live tracing ---
    @stream.where(ToolCallEvent).subscribe()
    async def trace_tools(event: ToolCallEvent) -> None:
        print(f"  [trace] tool call: {event.name}({event.arguments})")

    agent = Agent(
        "assistant",
        prompt="You are a helpful assistant. Answer in one sentence.",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        tools=[get_distance],
    )

    # --- 3. Run two turns on the same observed stream ---
    print("=== Session: two turns on one observed stream ===\n")
    reply = await agent.ask("What is the speed of light?", stream=stream)
    print(f"Turn 1: {reply.body}")

    reply2 = await agent.ask(
        "How far is Lisbon from Reykjavik? Use the tool.", stream=stream
    )
    print(f"Turn 2: {reply2.body}")

    # --- 4. Persist the captured event log ---
    with open(LOG_PATH, "w", encoding="utf-8") as handle:
        for event in log:
            handle.write(json.dumps(event.to_dict(), default=str) + "\n")
    print(f"\nWrote {len(log)} events to {LOG_PATH}")

    # --- 5. Query the captured session ---
    print("\n=== Event counts ===")
    for name, count in Counter(type(e).__name__ for e in log).most_common():
        print(f"  {name}: {count}")

    print("\n=== Token usage ===")
    totals: Counter[str] = Counter()
    for event in log:
        if isinstance(event, UsageEvent):
            totals["prompt"] += event.usage.prompt_tokens or 0
            totals["completion"] += event.usage.completion_tokens or 0
    print(f"  prompt tokens:     {totals['prompt']}")
    print(f"  completion tokens: {totals['completion']}")


if __name__ == "__main__":
    asyncio.run(main())
