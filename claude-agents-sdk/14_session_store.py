import asyncio

from dotenv import load_dotenv

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    InMemorySessionStore,
    list_sessions_from_store,
    get_session_messages_from_store,
)

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Claude Agent SDK with the following features:
- SessionStore adapter for pluggable transcript storage
- InMemorySessionStore as a reference implementation
- session_store option on ClaudeAgentOptions
- Listing sessions and reading messages from the store
- Eager session flushing with session_store_flush="eager"

SessionStore decouples transcript persistence from the local filesystem.
Instead of relying on on-disk JSONL files, you can mirror transcripts to
any backend (in-memory, S3, Redis, Postgres). This enables cross-host
resume, live-tailing UIs, and crash-durable storage.

For more details, visit:
https://platform.claude.com/docs/en/agent-sdk/session-storage
-------------------------------------------------------
"""

# --- 1. Create an in-memory session store ---
store = InMemorySessionStore()
print("=== Session Store Demo ===")
print(f"Store type: {type(store).__name__}")

# --- 2. Run a query with the session store attached ---
print("\n--- Step 1: Run a query with session mirroring ---")


async def run_with_store() -> str:
    session_id = ""

    options = ClaudeAgentOptions(
        session_store=store,
        session_store_flush="eager",  # Near-real-time transcript delivery
    )

    async for message in query(
        prompt="What are the three primary colors? Answer in one sentence.",
        options=options,
    ):
        if isinstance(message, ResultMessage):
            session_id = message.session_id
            if message.subtype == "success":
                print(f"Response: {message.result}")
                print(f"Session ID: {session_id}")

    return session_id


saved_id = asyncio.run(run_with_store())

# --- 3. List sessions from the store ---
print("\n--- Step 2: List sessions from store ---")


async def inspect_store(session_id: str):
    sessions = await list_sessions_from_store(store)
    print(f"Sessions in store: {len(sessions)}")
    for s in sessions:
        print(f"  - {s.id} (created: {s.created_at})")

    # --- 4. Read messages from the stored session ---
    print(f"\n--- Step 3: Read messages from session {session_id[:12]}... ---")
    messages = await get_session_messages_from_store(store, session_id)
    print(f"Total messages in transcript: {len(messages)}")
    for msg in messages:
        msg_type = type(msg).__name__
        preview = ""
        if isinstance(msg, ResultMessage) and msg.subtype == "success":
            preview = f" -> {msg.result[:60]}..."
        print(f"  [{msg_type}]{preview}")


asyncio.run(inspect_store(saved_id))
