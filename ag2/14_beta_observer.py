import asyncio
import os

from autogen.beta import Agent, MemoryStream
from autogen.beta.config import OpenAIConfig
from autogen.beta.events import ModelRequest, ModelResponse, ModelMessage

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2's Beta Agent with the following features:
- MemoryStream for event capture and observation
- Subscribing to agent events in real time
- Event types: ModelRequest, ModelMessage, ModelResponse

For more details, visit:
https://docs.ag2.ai/latest/docs/user-guide/release-roadmap/
-------------------------------------------------------
"""


async def main() -> None:
    agent = Agent(
        "assistant",
        "You are a helpful assistant. Reply in 1-2 sentences.",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
    )

    stream = MemoryStream()
    captured_events: list = []

    async def on_event(event: object) -> None:
        captured_events.append(event)
        event_name = type(event).__name__
        if isinstance(event, ModelRequest):
            print(f"  [Observer] {event_name}: LLM request sent")
        elif isinstance(event, ModelMessage):
            print(f"  [Observer] {event_name}: LLM message received")
        elif isinstance(event, ModelResponse):
            print(f"  [Observer] {event_name}: LLM response complete")
        else:
            print(f"  [Observer] {event_name}")

    stream.subscribe(on_event)

    print("=== Beta Agent: Observer API ===\n")
    print("Events as they happen:")
    reply = await agent.ask("What is the speed of light?", stream=stream)

    print(f"\nResponse: {reply.body}")

    print(f"\n=== Observer Summary ===")
    print(f"Total events captured: {len(captured_events)}")
    for i, event in enumerate(captured_events):
        print(f"  {i + 1}. {type(event).__name__}")


if __name__ == "__main__":
    asyncio.run(main())
