from dotenv import load_dotenv
from langgraph.store.memory import InMemoryStore

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- The CompositeBackend, which routes file paths to different backends
- Combining an ephemeral StateBackend with a persistent StoreBackend
- Routing by path prefix (longest-prefix match wins)

The virtual filesystem is pluggable. A CompositeBackend lets you mix
backends in a single filesystem: scratch files can live in ephemeral
per-thread state while anything under /memories/ is routed to a durable
store that survives across threads. This is the foundation for giving an
agent both short-term scratch space and long-term memory at once. Here we
write to both prefixes and show where each file actually landed.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/backends
-----------------------------------------------------------------------
"""

# --- 1. Build a composite backend: default state + /memories/ -> store ---
store = InMemoryStore()
backend = CompositeBackend(
    default=StateBackend(),  # ephemeral, lives in thread state
    routes={
        "/memories/": StoreBackend(namespace=lambda ctx: ("memories",)),  # durable store
    },
)

# --- 2. Create the agent with the composite backend and a store ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    backend=backend,
    store=store,
    system_prompt=(
        "You have a virtual filesystem. Write exactly the files the user asks for, "
        "then confirm in one sentence."
    ),
)

# --- 3. Ask the agent to write to both a scratch path and a memories path ---
print("=== Deep Agents Composite Backend ===")
task = "Write /scratch.txt with 'temporary note', and write /memories/profile.txt with 'the user prefers tea'."
result = agent.invoke({"messages": [{"role": "user", "content": task}]})

# --- 4. Show routing: state-backed files vs store-backed files ---
state_files = list(result.get("files", {}).keys())
print(f"\nStateBackend (ephemeral, thread state): {state_files}")

print("StoreBackend (durable, /memories/ route):")
for ns in store.list_namespaces():
    for item in store.search(ns):
        print(f"  namespace={ns} key={item.key} content={item.value['content']!r}")

# --- 5. Print the agent's confirmation ---
print(f"\nAgent: {result['messages'][-1].text}")
