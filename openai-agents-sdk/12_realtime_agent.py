import asyncio
import os
from agents import function_tool
from agents.realtime import RealtimeAgent, RealtimeRunner
from agents.realtime.items import AssistantMessageItem
from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------------------------
In this example, we explore Realtime Agents — server-side, low-latency
agents built on the OpenAI Realtime API over WebSocket transport.

Features demonstrated:
- RealtimeAgent with custom instructions
- RealtimeRunner with model and audio configuration
- Function tools in realtime agents
- Server-side WebSocket session with event streaming
- Text-based interaction (no microphone needed for this demo)

Realtime Agents are unique to the OpenAI Agents SDK. They enable
voice-first AI experiences with sub-second latency, automatic
turn detection, and the same tool/handoff patterns as text agents.

Note: This example uses text messages for demonstration purposes.
For voice/audio, you would send PCM16 audio chunks via
session.send_audio() and handle audio events from the stream.
-------------------------------------------------------------------------
"""


# 1. Define tools that the realtime agent can use
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Simulated weather data
    weather_data = {
        "san francisco": "62°F, foggy",
        "new york": "75°F, sunny",
        "london": "58°F, cloudy",
        "tokyo": "82°F, humid",
    }
    return weather_data.get(city.lower(), f"Weather data not available for {city}")


@function_tool
def get_time(timezone: str) -> str:
    """Get the current time in a timezone."""
    # Simulated time data
    time_data = {
        "pst": "10:30 AM PST",
        "est": "1:30 PM EST",
        "gmt": "6:30 PM GMT",
        "jst": "3:30 AM JST (next day)",
    }
    return time_data.get(timezone.lower(), f"Time not available for {timezone}")


async def main():
    print("=== Realtime Agent Example ===\n")

    # 2. Define a RealtimeAgent (similar to Agent, but for realtime sessions)
    agent = RealtimeAgent(
        model="gpt-4o-mini-realtime-preview",
        name="Voice Assistant",
        instructions=(
            "You are a helpful voice assistant. Keep responses short and "
            "conversational. You can check weather and time for the user."
        ),
        tools=[get_weather, get_time],
    )

    # 3. Configure the RealtimeRunner
    #    By default, the runner connects via WebSocket to the Realtime API.
    #    Audio config is optional — the model will produce audio output
    #    and we extract the transcript for this text-based demo.
    runner = RealtimeRunner(starting_agent=agent)

    # 4. Start the realtime session
    print("Starting realtime session via WebSocket...")
    print("(Using text messages for this demo — voice uses send_audio())\n")

    session = await runner.run()

    async with session:
        # 5. Send a text message (in production, you'd stream audio)
        print("User: What's the weather in San Francisco?\n")
        await session.send_message("What's the weather in San Francisco?")

        # 6. Stream events from the session
        #    The Realtime API produces audio by default. After the model calls
        #    a tool and generates a response, the transcript appears in the
        #    history_updated event. We track agent_end events to know when
        #    both the tool-call turn and response turn have completed.
        print("Assistant: ", end="", flush=True)
        agent_ends = 0
        responded = False
        async for event in session:
            if event.type == "audio":
                # In a real app, you'd forward audio bytes to speakers
                pass
            elif event.type == "tool_start":
                print(f"[calling {event.tool.name}({event.arguments})]", flush=True)
            elif event.type == "tool_end":
                print(f"[tool result: {event.output}]", flush=True)
            elif event.type == "history_updated":
                # The transcript is populated in history_updated (not history_added)
                for item in event.history:
                    if isinstance(item, AssistantMessageItem):
                        for content in item.content:
                            transcript = getattr(content, "transcript", None)
                            text = getattr(content, "text", None)
                            value = transcript or text
                            if value and not responded:
                                print(value, flush=True)
                                responded = True
            elif event.type == "agent_end":
                agent_ends += 1
                if agent_ends >= 2 or responded:
                    break
            elif event.type == "error":
                print(f"\nError: {event}")
                break

    print("\n=== Realtime Agent Demo Complete ===")
    print("In production, connect microphone input and speaker output")
    print("for a full voice conversation experience.")


if __name__ == "__main__":
    asyncio.run(main())
