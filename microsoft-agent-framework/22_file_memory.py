import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from agent_framework import (
    Agent,
    AgentResponse,
    AgentSession,
    FileMemoryProvider,
    FileSystemAgentFileStore,
)
from agent_framework.openai import OpenAIChatClient

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Microsoft Agent Framework
with the following features:
- FileMemoryProvider as a context provider for long-term memory
- FileSystemAgentFileStore to persist memories as real files
- scope="users/<id>" to share one memory folder across sessions
- Model-driven file_memory_write / file_memory_read tools

Unlike an AgentSession (example 04), which only remembers the
current conversation, file memory lives outside the transcript. The
model decides what is worth writing, and a stable scope lets a
brand-new session read it back — the mechanism the harness agent
(example 21) uses internally.

For more details, visit:
https://learn.microsoft.com/en-us/agent-framework/agents/harness
-------------------------------------------------------
"""

USER_ID = "UID1"
MEMORY_ROOT = Path("res") / "agent-file-memory"


def print_memory_tool_calls(result: AgentResponse) -> None:
    """Prints the file_memory_* tools the model chose to call."""
    calls = [
        content.name
        for message in result.messages
        for content in message.contents
        if content.type == "function_call" and str(content.name).startswith("file_memory")
    ]
    print(f"Memory tools called: {calls or 'none'}")


async def main() -> None:
    # --- 1. Create the store that holds the memory files ---
    os.makedirs(MEMORY_ROOT, exist_ok=True)
    store = FileSystemAgentFileStore(MEMORY_ROOT)

    # --- 2. Scope the provider to a user, not to a session ---
    # Omitting scope would derive the working folder from the session id,
    # which isolates memories per conversation. A stable per-user scope is
    # what makes the second session below able to read the first one's notes.
    memory = FileMemoryProvider(store, scope=f"users/{USER_ID}")

    client = OpenAIChatClient(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    agent = Agent(
        client=client,
        name="travel-assistant",
        instructions=(
            "You are a travel assistant. Save durable facts the user tells you "
            "about themselves with your memory tools, and consult them before "
            "making recommendations. Answer in 1-2 sentences."
        ),
        context_providers=[memory],
    )

    working_folder = MEMORY_ROOT / "users" / USER_ID
    print(f"Memory folder: {working_folder}\n")

    # --------------------------------------------------------------
    # Example 1: First session — the agent writes what it learns
    # --------------------------------------------------------------
    print("=== Session 1: teach the agent something ===")
    first_session: AgentSession = agent.create_session()
    result = await agent.run(
        "I'm vegetarian and I always travel with my dog. Remember that for future trips.",
        session=first_session,
    )
    print(f"Agent: {result.text}")
    print_memory_tool_calls(result)

    # --- 3. The memories are ordinary files on disk ---
    print("\n=== Memory files written ===")
    for path in sorted(working_folder.rglob("*")):
        if path.is_file():
            print(f"- {path.relative_to(working_folder)}")

    # --------------------------------------------------------------
    # Example 2: A brand-new session with no shared chat history
    # --------------------------------------------------------------
    print("\n=== Session 2: new session, no shared transcript ===")
    second_session: AgentSession = agent.create_session()
    result = await agent.run(
        "Book me a hotel and a dinner spot in Paris. What should I watch out for?",
        session=second_session,
    )
    print(f"Agent: {result.text}")
    print_memory_tool_calls(result)

    # --- 4. Prove the two conversations really were separate ---
    print(f"\nSession 1 id: {first_session.session_id}")
    print(f"Session 2 id: {second_session.session_id}")
    print(f"Shared scope: users/{USER_ID}")


if __name__ == "__main__":
    asyncio.run(main())
