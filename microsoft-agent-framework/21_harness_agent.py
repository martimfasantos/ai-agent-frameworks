import asyncio

from dotenv import load_dotenv

from agent_framework import create_harness_agent
from agent_framework.openai import OpenAIChatClient

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Microsoft Agent Framework
with the following features:
- create_harness_agent: batteries-included agent factory
- Built-in memory store for persistent context
- Built-in todo management for task tracking
- Built-in mode switching (e.g., concise vs verbose)
- Automatic context window compaction

The harness agent (new in v1.5+) wraps a standard agent with
production-ready capabilities: memory, todos, modes, skills,
and web search. It handles context window management automatically
and provides a structured agent experience out of the box.

For more details, visit:
https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-python
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
        agent_instructions="You are a helpful assistant. Be concise.",
        max_context_window_tokens=128000,
        max_output_tokens=4096,
        disable_web_search=True,  # Disable web search for this demo
    )

    # --- Run the agent ---
    print("=== Harness Agent Demo ===\n")

    # Turn 1: The agent will remember this
    response = await agent.run("My project deadline is next Friday.")
    print(f"Turn 1: {response.text}\n")

    # Turn 2: The agent should recall the deadline
    response = await agent.run("When is my deadline?")
    print(f"Turn 2: {response.text}\n")

    print("=== Harness Agent Features ===")
    print("- Memory: persists facts across turns")
    print("- Todos: agent can track tasks (try: 'add a todo to review the PR')")
    print("- Modes: switch between concise/verbose (try: 'switch to verbose mode')")
    print("- Compaction: auto-manages context window size")


if __name__ == "__main__":
    asyncio.run(main())
