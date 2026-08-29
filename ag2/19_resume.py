import asyncio
import os

from ag2 import Agent
from ag2.config import OpenAIConfig
from ag2.events import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextInput,
    ToolCallEvent,
    ToolCallsEvent,
    ToolResultEvent,
    ToolResultsEvent,
)

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- agent.resume(*events, trigger) to rebuild a conversation
- Resuming from a stored trajectory with a new user message
- Resuming mid-loop from a ToolResultsEvent produced out of band

ask() starts a turn from the agent's live stream; resume() starts
one from a recorded trajectory. All events except the last seed the
history, and the last event is the trigger that drives the next LLM
call. This is how a turn survives a process restart, or continues on
a different worker once a webhook delivers a tool result.

For more details, visit:
https://docs.ag2.ai/latest/docs/beta/resume/
-------------------------------------------------------
"""


async def main() -> None:
    agent = Agent(
        "assistant",
        prompt="You are a helpful travel assistant. Answer in one sentence.",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
    )

    # --- 1. Run a turn, then capture its trajectory as plain events ---
    print("=== Step 1: an original conversation ===")
    reply = await agent.ask("Plan a two-day trip to Kyoto.")
    print(f"Agent: {reply.body}")

    stored = list(await reply.context.stream.history.get_events())
    print(f"\nStored trajectory: {len(stored)} events")
    print(f"  {[type(e).__name__ for e in stored]}")

    # --- 2. Resume it later (or in another process) with a new trigger ---
    # A fresh Agent object with no live stream: everything it knows comes
    # from the events we hand it.
    print("\n=== Step 2: resume from the stored trajectory ===")
    revived = Agent(
        "assistant",
        prompt="You are a helpful travel assistant. Answer in one sentence.",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
    )
    trigger = ModelRequest([TextInput("And what about getting there by train?")])
    resumed = await revived.resume(*stored, trigger)
    print(f"Agent: {resumed.body}")

    # --- 3. Resume mid-loop from a tool result produced elsewhere ---
    # The model asked for a tool call; the result came from a webhook or
    # queue worker, so we replay the call and hand back its result.
    print("\n=== Step 3: resume from an out-of-band tool result ===")
    support = Agent(
        "support",
        prompt="Answer the customer using the tool result. One sentence.",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
    )

    call = ToolCallEvent(name="lookup_order", arguments='{"id": "A-1001"}', id="call-1")
    history = [
        ModelRequest([TextInput("Where is order A-1001?")]),
        ModelResponse(message=ModelMessage(""), tool_calls=ToolCallsEvent([call])),
    ]
    tool_result = ToolResultsEvent(
        [ToolResultEvent.from_call(call, "Shipped, arriving Tuesday.")]
    )

    grounded = await support.resume(*history, tool_result)
    print("  replayed call:  lookup_order(id=A-1001)")
    print("  out-of-band result: 'Shipped, arriving Tuesday.'")
    print(f"  Agent: {grounded.body}")


if __name__ == "__main__":
    asyncio.run(main())
