import asyncio

from dotenv import load_dotenv

from agent_framework import InMemoryAgentFileStore, create_harness_agent
from agent_framework.openai import OpenAIChatClient

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Microsoft Agent Framework
with the following features:
- create_harness_agent: batteries-included agent factory
- Built-in file memory for persistent context
- Built-in todo management for task tracking
- Built-in mode switching (e.g., concise vs verbose)
- Automatic context window compaction

The harness agent wraps a standard agent with production-ready
capabilities: memory, todos, modes, skills, and web search. Its
built-in tools are approval-gated, so the harness requires an
AgentSession — reusing one session is also what lets file memory
recall facts from earlier turns.

For more details, visit:
https://learn.microsoft.com/en-us/agent-framework/agents/harness
-------------------------------------------------------
"""


async def main() -> None:
    # --- Create the OpenAI client ---
    client = OpenAIChatClient(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    # --- Create a harness agent with built-in capabilities ---
    agent = create_harness_agent(
        client=client,
        id="harness-demo",
        name="Harness Assistant",
        description="A demo agent with memory, todos, and modes.",
        agent_instructions=(
            "You are a helpful assistant. Answer in one short sentence using only "
            "facts the user gave you. Never ask follow-up questions, never build "
            "a plan, and never invent calendar dates."
        ),
        max_context_window_tokens=128000,
        max_output_tokens=4096,
        disable_web_search=True,  # Disable web search for this demo
        # Without this the harness falls back to a FileSystemAgentFileStore
        # rooted at ./agent-file-memory — keep the demo entirely in memory.
        file_memory_store=InMemoryAgentFileStore(),
        # Keep the transcript client-side so the harness history provider — not
        # a service-managed conversation — is what carries the earlier turn.
        default_options={"store": False},
    )

    # --- Run the agent ---
    print("=== Harness Agent Demo ===\n")

    # One session for both turns: the harness needs it for tool approval, and
    # file memory scopes its working folder by session id.
    session = agent.create_session()

    # Turn 1: The agent will remember this
    response = await agent.run("My project deadline is next Friday.", session=session)
    print(f"Turn 1: {response.text}\n")

    # Turn 2: The agent should recall the deadline
    response = await agent.run("When is my deadline?", session=session)
    print(f"Turn 2: {response.text}\n")

    print("=== Harness Agent Features ===")
    print("- Memory: persists facts across turns in the same session")
    print("- Todos: agent can track tasks (try: 'add a todo to review the PR')")
    print("- Modes: switch between concise/verbose (try: 'switch to verbose mode')")
    print("- Compaction: auto-manages context window size")


if __name__ == "__main__":
    asyncio.run(main())
