from dotenv import load_dotenv

from deepagents import create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Streaming a run incrementally with agent.stream(...)
- Using stream_mode="updates" to see each step as it happens
- Watching tool calls and messages arrive in real time

Long-running agents shouldn't feel like a black box. The stream() method
yields incremental updates as the agent thinks, calls tools, and produces
its answer, so you can surface progress to users immediately instead of
waiting for the whole run to finish. Here we stream a tool-using run and
print each update as it arrives.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/event-streaming
-----------------------------------------------------------------------
"""


# --- 1. Define a simple tool ---
def get_population(city: str) -> str:
    """Get the approximate population of a given city."""
    data = {"tokyo": "37 million", "lisbon": "3 million", "cairo": "22 million"}
    return data.get(city.lower(), "unknown")


# --- 2. Create the agent ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    tools=[get_population],
    system_prompt="You are a geography assistant. Use tools and answer in one sentence.",
)

# --- 3. Stream the run with stream_mode="updates" ---
print("=== Deep Agents Streaming ===")
question = "Which is bigger by population, Tokyo or Cairo?"
print(f"User: {question}\n")
print("Streaming updates as they arrive:")

final_answer = ""
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="updates",
):
    # Each chunk maps a node name to its state update
    for node, update in chunk.items():
        messages = update.get("messages", []) if isinstance(update, dict) else []
        for msg in messages:
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                for tc in tool_calls:
                    print(f"  [{node}] tool call -> {tc['name']}({tc['args']})")
            elif getattr(msg, "type", None) == "tool":
                print(f"  [{node}] tool result -> {msg.content}")
            elif getattr(msg, "text", ""):
                final_answer = msg.text

# --- 4. Print the final streamed answer ---
print(f"\nAgent: {final_answer}")
