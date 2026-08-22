from dotenv import load_dotenv
from langgraph.store.memory import InMemoryStore

from deepagents import create_deep_agent
from deepagents.backends import StoreBackend

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- StoreBackend: durable file storage backed by a LangGraph store
- Persistence that outlives a single conversation / agent instance
- Reading back in a second conversation what a first one wrote

The default StateBackend keeps files in per-conversation thread state, so
they vanish between runs. The StoreBackend instead persists files in a
LangGraph store (here an in-memory store, but in production a database).
Because the store is shared, a completely separate conversation can read
files an earlier one saved. We prove it by writing in conversation 1 and
reading it back with a fresh agent in conversation 2.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/backends
-----------------------------------------------------------------------
"""

# --- 1. Create a durable store and a StoreBackend that uses it ---
store = InMemoryStore()
backend = StoreBackend(store=store, namespace=lambda ctx: ("user_data",))


def make_agent():
    """Each call is an independent conversation, but all share one store."""
    return create_deep_agent(
        model=f"openai:{settings.OPENAI_MODEL_NAME}",
        backend=backend,
        store=store,
        system_prompt="You are a note keeper. Use files to remember things.",
    )


print("=== Deep Agents Store Backend ===")

# --- 2. Conversation 1: save a preference to the store ---
agent1 = make_agent()
result1 = agent1.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Save a file preferences.txt with exactly: favorite color is teal",
            }
        ]
    }
)
print(f"\n[Conversation 1 - write] Agent: {result1['messages'][-1].text}")

# --- 3. Inspect the durable store directly ---
print("\nFiles now living in the durable store:")
for item in store.search(("user_data",)):
    print(f"  key={item.key} content={item.value.get('content')!r}")

# --- 4. Conversation 2: a brand-new agent reads the persisted file ---
agent2 = make_agent()
result2 = agent2.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Read preferences.txt and tell me my favorite color.",
            }
        ]
    }
)
print(f"\n[Conversation 2 - read] Agent: {result2['messages'][-1].text}")
print("\n(Conversation 2 had no shared message history — only the store persisted it.)")
