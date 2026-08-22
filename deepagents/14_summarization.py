from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.middleware.summarization import (
    SummarizationMiddleware,
    SummarizationToolMiddleware,
)

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Conversation summarization to keep the context window small
- The compact_conversation tool (SummarizationToolMiddleware)
- Supplying the compaction system_prompt, which no longer has a default
- A low token trigger so compaction is demonstrable in a short run

Long-running agents accumulate huge message histories that inflate cost
and latency. Deep Agents can summarize older turns into a compact summary,
freeing context while preserving the important facts. Here we wire up the
on-demand compact_conversation tool with a deliberately low token trigger,
fill the conversation with detail, then ask the agent to compact — and the
tool reports exactly how many messages it folded into a summary.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/context-engineering
-----------------------------------------------------------------------
"""

# --- 1. Build a summarization middleware with a low trigger for the demo ---
model = ChatOpenAI(model=settings.OPENAI_MODEL_NAME)
backend = StateBackend()
summarization = SummarizationMiddleware(
    model,
    backend=backend,
    trigger=("tokens", 200),  # tiny threshold so we can trigger it cheaply
    keep=("messages", 2),  # always retain the 2 most recent messages verbatim
)

# --- 2. Expose it as an on-demand compact_conversation tool ---
# system_prompt defaults to None since 0.7.0, so the nudge must be passed explicitly
compaction_tool = SummarizationToolMiddleware(
    summarization,
    system_prompt=(
        "When the current topic is finished, or the conversation has grown long, "
        "call compact_conversation to fold the older turns into a summary."
    ),
)
agent = create_deep_agent(
    model=model,
    middleware=[compaction_tool],
    system_prompt="You are a helpful assistant.",
)

print("=== Deep Agents Summarization ===")

# --- 3. Fill the conversation with detail so it exceeds the token trigger ---
detail = (
    "The project codename is Bluefin, launch date March 14, budget is 2 "
    "million euros, lead engineer is Dana, primary market is Iberia. "
) * 6
result1 = agent.invoke(
    {"messages": [{"role": "user", "content": detail + " Acknowledge in one short sentence."}]}
)
print(f"\nMessages after a detailed turn: {len(result1['messages'])}")

# --- 4. Ask the agent to compact the now-bloated conversation ---
conversation = result1["messages"] + [
    {
        "role": "user",
        "content": "We're done with that topic. Call compact_conversation now to refresh context.",
    }
]
result2 = agent.invoke({"messages": conversation})

# --- 5. Show the compaction tool call and its result ---
for msg in result2["messages"]:
    if msg.type == "ai" and msg.tool_calls:
        for tc in msg.tool_calls:
            print(f"\n[agent called tool] {tc['name']}")
    if msg.type == "tool":
        print(f"[tool result] {msg.text}")

print(f"\nAgent: {result2['messages'][-1].text}")
