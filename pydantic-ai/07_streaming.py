import asyncio
from collections.abc import AsyncIterable
from datetime import date

from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import (
    AgentStreamEvent,
    FinalResultEvent,
    FunctionToolCallEvent,
)

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Streaming text output using a custom handler
- Streaming all events and then parsing

This example demonstrates real-time streaming capabilities with Pydantic AI.
Streaming allows you to receive and process AI responses as they're generated,
providing better user experience for real-time applications and allowing
for observability of the agent's internal behaviour.

For more details, visit:
https://pydantic.dev/docs/ai/core-concepts/output/#streaming-text
-----------------------------------------------------------------------
"""

# --- 1. Define the Agent ---
weather_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions="Provide weather information using the weather tool. Be concise, reply in 1-2 sentences.",
)


# --- 2. Define an example tool ---
@weather_agent.tool
async def get_weather(ctx: RunContext, location: str, date: date) -> str:
    """Get weather forecast for a location and date."""
    return f"The weather in {location} on {date} will be sunny and 24°C"


# --- 3. Event Stream Handler (receives context + async iterable of events) ---
async def handle_stream_events(
    ctx: RunContext, events: AsyncIterable[AgentStreamEvent]
) -> None:
    """Handle different types of streaming events."""
    async for event in events:
        if isinstance(event, FinalResultEvent):
            print(f"[EVENT] Final result started (tool: {event.tool_name})")
        elif isinstance(event, FunctionToolCallEvent):
            print(
                f"[EVENT] Tool called: {event.part.tool_name} with args: {event.part.args}"
            )


# --- 4. Run Examples ---
async def main():

    print("\n=== Streaming with Custom Handler ===")
    async with weather_agent.run_stream(
        user_prompt="What will the weather be like in Paris tomorrow?",
        event_stream_handler=handle_stream_events,
    ) as result:
        async for text_chunk in result.stream_text():
            print(text_chunk, end="", flush=True)
    print("\n")

    print("\n=== Stream All Events and filtering ===")
    # run_stream_events() is an async context manager in v2; the returned
    # object is the event stream to iterate over.
    messages = []
    async with weather_agent.run_stream_events("Weather in Tokyo please") as events:
        async for event in events:
            if isinstance(event, FinalResultEvent):
                messages.append(f"Final result event: {event.tool_name}")
            elif isinstance(event, FunctionToolCallEvent):
                messages.append(f"Tool call: {event.part.tool_name}")

    for message in messages:
        print(f"[STREAM EVENT] {message}")


if __name__ == "__main__":
    asyncio.run(main())
