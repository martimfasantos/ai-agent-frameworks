import asyncio
import os
from collections import Counter

from langchain.agents import AgentState, create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore LangChain with the following features:
- v3 event streaming via astream_events(version="v3")
- Typed projections: stream.messages, message.text, message.tool_calls, stream.output
- stream.subgraphs to observe a nested graph run from the parent stream
- Raw protocol-event iteration as the escape hatch

The v3 streaming protocol exposes typed projections over one run, so you pick
the view you need instead of branching on stream_mode chunks: message.text
yields tokens, message.tool_calls yields tool-call argument chunks, and
stream.output awaits the final state. Iterating the stream object directly still
gives you the raw method/params envelopes when a projection does not cover
your case. A projection can only be consumed once per run.

For more details, visit:
https://docs.langchain.com/oss/python/langchain/streaming
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

# --- 3. Wrap the agent in a parent graph so it runs as a subgraph ---
parent_graph = (
    StateGraph(AgentState)
    .add_node("city_agent", agent)
    .add_edge(START, "city_agent")
    .add_edge("city_agent", END)
    .compile()
)

QUESTION = "What's the weather and population of Lisbon?"


# --------------------------------------------------------------
# Example 1: typed projections (the recommended path)
# --------------------------------------------------------------
async def typed_projections() -> None:
    print("=== Example 1: typed projections ===")

    stream = await agent.astream_events(
        {"messages": [{"role": "user", "content": QUESTION}]},
        version="v3",
    )

    # --- 4. stream.messages yields one handle per model message ---
    async for message in stream.messages:
        print(f"  [{message.node}] ", end="", flush=True)

        # message.text streams the answer token by token
        async for token in message.text:
            print(token, end="", flush=True)

        # message.tool_calls streams tool-call argument chunks as they arrive
        chunks = [chunk async for chunk in message.tool_calls]
        tool_calls = message.output_message.tool_calls
        if tool_calls:
            print(f"{len(chunks)} tool-call argument chunks streamed:")
            for call in tool_calls:
                print(f"    -> {call['name']}({call['args']})")
        else:
            print()

    # --- 5. stream.output awaits the final state once the run is done ---
    final_state = await stream.output()
    for message in final_state["messages"]:
        if message.type == "tool":
            print(f"  tool result {message.name} -> {message.content}")
    print(f"  final answer: {final_state['messages'][-1].text}\n")


# --------------------------------------------------------------
# Example 2: stream.subgraphs for nested runs
# --------------------------------------------------------------
async def subgraph_projection() -> None:
    print("=== Example 2: stream.subgraphs ===")

    stream = await parent_graph.astream_events(
        {"messages": [{"role": "user", "content": "What's the weather in Tokyo?"}]},
        version="v3",
    )

    # --- 6. Each subgraph handle carries its own projections ---
    async for subgraph in stream.subgraphs:
        print(f"  subgraph '{subgraph.graph_name}' status={subgraph.status}")
        async for message in subgraph.messages:
            text = "".join([token async for token in message.text])
            if text:
                print(f"    [{subgraph.graph_name}] {text}")
    print()


# --------------------------------------------------------------
# Example 3: raw protocol events (the escape hatch)
# --------------------------------------------------------------
async def raw_events() -> None:
    print("=== Example 3: raw protocol events (escape hatch) ===")

    stream = await agent.astream_events(
        {"messages": [{"role": "user", "content": QUESTION}]},
        version="v3",
    )

    # --- 7. Iterating the stream itself yields the method/params envelopes ---
    methods: Counter[str] = Counter()
    async for event in stream:
        methods[event["method"]] += 1

    for method, count in sorted(methods.items()):
        print(f"  {method:<12} {count} events")


async def main() -> None:
    await typed_projections()
    await subgraph_projection()
    await raw_events()


if __name__ == "__main__":
    asyncio.run(main())
