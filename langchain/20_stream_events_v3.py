import asyncio
import os

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore LangChain with the following features:
- v3 event streaming via astream_events(version="v3")
- Granular event types: tool-started, tool-finished, content-block-delta
- Real-time observation of agent execution steps

The v3 event streaming API (new in langchain 1.3.0) provides
structured events for every step of agent execution — model
tokens, tool calls, and chain lifecycle. This enables building
real-time UIs that show tool usage and streaming responses.

For more details, visit:
https://python.langchain.com/docs/how_to/streaming/
-------------------------------------------------------
"""


# --- 1. Define tools ---
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    data = {"lisbon": "Sunny, 26°C", "london": "Cloudy, 15°C", "tokyo": "Rainy, 20°C"}
    return data.get(city.lower(), f"No weather data for {city}")


@tool
def get_population(city: str) -> str:
    """Get the population of a city."""
    data = {"lisbon": "550,000", "london": "8,800,000", "tokyo": "13,900,000"}
    return data.get(city.lower(), f"No population data for {city}")


# --- 2. Create agent ---
llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=0)

agent = create_agent(
    model=llm,
    tools=[get_weather, get_population],
    system_prompt="You are a helpful assistant. Be concise, reply in 1-2 sentences.",
)


# --- 3. Stream events with version="v3" ---
async def main() -> None:
    print("=== v3 Event Streaming ===")
    print()

    events_seen: list[str] = []

    async for event in await agent.astream_events(
        {"messages": [{"role": "user", "content": "What's the weather and population of Lisbon?"}]},
        version="v3",
    ):
        method = event.get("method", "")
        data = event.get("params", {}).get("data", {})

        # Tool events
        if method == "tools":
            inner_event = data.get("event", "")
            if inner_event == "tool-started":
                tool_name = data.get("tool_name", "")
                tool_input = data.get("input", {})
                print(f"[Tool Start] {tool_name}({tool_input})")
                events_seen.append(f"tool-started:{tool_name}")
            elif inner_event == "tool-finished":
                tool_name = data.get("tool_call_id", "")
                output = data.get("output", "")
                content = getattr(output, "content", str(output))
                # Get tool name from the output message
                name = getattr(output, "name", tool_name)
                print(f"[Tool End]   {name} -> {content}")
                events_seen.append(f"tool-finished:{name}")

        # Message streaming events
        elif method == "messages" and isinstance(data, tuple) and len(data) >= 1:
            msg_data = data[0]
            if isinstance(msg_data, dict):
                inner_event = msg_data.get("event", "")
                if inner_event == "content-block-delta":
                    delta = msg_data.get("delta", {})
                    # Text content streaming (type="text-delta")
                    if delta.get("type") == "text-delta":
                        text = delta.get("text", "")
                        print(text, end="", flush=True)
                elif inner_event == "message-start":
                    events_seen.append("message-start")
                elif inner_event == "message-finish":
                    events_seen.append("message-finish")

    print()  # newline after streaming
    print()

    # --- 4. Summary of events captured ---
    print("=== Events Captured ===")
    for e in events_seen:
        print(f"  {e}")


if __name__ == "__main__":
    asyncio.run(main())
