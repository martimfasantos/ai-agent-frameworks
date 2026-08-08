import asyncio
import json
import os

from strands import Agent
from strands.memory import IntervalTrigger, MemoryManager
from strands.models.openai import OpenAIModel
from strands.vended_memory_stores.test_memory_store import TestMemoryStore

from settings import settings

"""
-------------------------------------------------------
In this example, we explore Strands Agents SDK with the following features:
- MemoryManager, the cross-session memory subsystem (new in v1.43.0)
- TestMemoryStore, a zero-infrastructure store backed by a local JSON file
- add_tool_config=True to give the agent an add_memory tool
- Automatic extraction via IntervalTrigger, plus store.add() / store.search()

Memory stores EXTRACTED FACTS, not transcripts: a second agent with an empty
message history still knows the user's preferences because the manager searches
the store and injects matches into the prompt. This is the complement of
17_session_persistence.py, which replays the conversation history itself.

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/memory/test-memory-store/
-------------------------------------------------------
"""

# TestMemoryStore defaults to ~/.strands/memory/<name>.json — point it at res/ instead.
MEMORY_PATH = "res/notes.json"

openai_model = OpenAIModel(
    client_args={
        "api_key": settings.OPENAI_API_KEY.get_secret_value()
        if settings.OPENAI_API_KEY
        else ""
    },
    model_id=settings.OPENAI_MODEL_NAME,
)


# --- 1. Build a store and a manager over the same JSON file ---
def build_memory() -> tuple[TestMemoryStore, MemoryManager]:
    """Create a fresh store/manager pair pointing at the shared JSON file."""
    store = TestMemoryStore(
        name="notes",
        description="Durable facts about the user and their team.",
        path=MEMORY_PATH,
        # Distil facts out of the conversation after every turn (default: every 5).
        extraction={"trigger": IntervalTrigger(turns=1)},
    )
    manager = MemoryManager(
        stores=[store],
        add_tool_config=True,  # exposes an add_memory tool to the agent
    )
    return store, manager


def show_file() -> None:
    """Print the contents of the JSON file backing the store."""
    with open(MEMORY_PATH) as f:
        records = json.load(f)
    print(f"  {MEMORY_PATH} holds {len(records)} record(s):")
    for record in records:
        print(f"    - {record['content']}")


async def main() -> None:
    os.makedirs("res", exist_ok=True)
    if os.path.exists(MEMORY_PATH):
        os.remove(MEMORY_PATH)  # start from a clean slate on every run

    print("=== Agent Memory: Extracted Facts Across Sessions ===\n")

    # --- 2. Session 1: the agent writes memories with the add_memory tool ---
    print("--- Session 1: writing memories ---")
    store, memory = build_memory()
    agent = Agent(
        model=openai_model,
        system_prompt="You are a helpful assistant. Be concise.",
        memory_manager=memory,
        callback_handler=None,
    )

    result = await agent.invoke_async(
        "Remember two things about me: I prefer metric units, "
        "and my team ships releases on Tuesdays."
    )
    print(f"Agent: {result.message['content'][0]['text']}")
    await memory.flush()  # wait for background extraction to finish
    show_file()
    print("  (written by the add_memory tool; extraction may restate them in its own words)")

    # --- 3. Automatic extraction: an ordinary turn, no 'remember' instruction ---
    print("\n--- Automatic extraction from a plain conversational turn ---")
    await agent.invoke_async("By the way, I'm based in Lisbon. Acknowledge in five words.")
    await memory.flush()
    show_file()
    print()

    # --- 4. Session 2: a brand-new agent with no conversation history ---
    print("--- Session 2: recall with an empty message history ---")
    _, memory_2 = build_memory()
    agent_2 = Agent(
        model=openai_model,
        system_prompt="You are a helpful assistant. Be concise.",
        memory_manager=memory_2,
        callback_handler=None,
    )
    print(f"Messages in history before asking: {len(agent_2.messages)}")

    result = await agent_2.invoke_async(
        "Which units should you use with me, and which day do we ship releases?"
    )
    print(f"Agent: {result.message['content'][0]['text']}\n")

    # --- 5. Direct store API: add and search outside any agent turn ---
    print("--- Direct store API ---")
    added = await store.add(
        "The on-call rotation handover happens every Monday at 09:00 WET.",
        metadata={"source": "runbook"},
    )
    print(f"store.add() -> id={added.id}")

    for entry in await store.search("when does the handover happen"):
        print(f"store.search() -> {entry.content}")
        print(f"  metadata: {entry.metadata}")
    print()

    # --- 6. Summary ---
    print("--- Summary ---")
    print("MemoryManager knobs:")
    print("  search_tool_config -> gives the agent a search tool (on by default)")
    print("  add_tool_config    -> gives the agent an add_memory tool (off by default)")
    print("  injection          -> auto-searches and injects matches per turn (on by default)")
    print("Store config: extraction={'trigger': IntervalTrigger(turns=N)} distils facts")
    print("from the transcript using the host agent's model — no extra provider needed.")
    print("_relevanceScore in search metadata is the lexical token-overlap score.")


if __name__ == "__main__":
    asyncio.run(main())
