import asyncio
import os

from ag2 import Agent, MemoryStream
from ag2.config import OpenAIConfig
from ag2.events import ToolCallEvent

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- Nesting subagents two levels deep to encapsulate a workflow
- A shared MemoryStream to observe the inner workflow's events
- The outer caller seeing a single tool, not the whole team

Classic AG2's register_nested_chats() has no direct successor.
The 1.0 idiom is a hierarchy of as_tool() subagents: the lead agent
delegates to a fact checker and an editor, and is itself exposed to
the caller as one tool. Passing an explicit stream to as_tool() lets
us read the encapsulated workflow's events afterwards.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/subagents.mdx
-------------------------------------------------------
"""


async def main() -> None:
    config = OpenAIConfig(model=settings.OPENAI_MODEL_NAME)

    # --- 1. Inner workflow agents ---
    fact_checker = Agent(
        "fact_checker",
        prompt=(
            "You are a fact checker. Verify the claim you are given and list "
            "2-3 verified points. Be concise."
        ),
        config=config,
    )

    editor = Agent(
        "editor",
        prompt=(
            "You are an editor. Polish the fact-checked notes you are given "
            "into a 2-3 sentence summary."
        ),
        config=config,
    )

    # --- 2. The lead agent owns the inner workflow ---
    lead = Agent(
        "lead_agent",
        prompt=(
            "You run a content pipeline. Always fact-check the topic first, "
            "then pass the verified notes to the editor via the context "
            "parameter. Return only the editor's final summary."
        ),
        config=config,
        tools=[
            fact_checker.as_tool(description="Fact-check a claim or topic."),
            editor.as_tool(
                description="Polish notes into a summary. Pass notes in the context parameter."
            ),
        ],
    )

    # --- 3. Expose the whole pipeline to the caller as ONE tool ---
    # The explicit stream makes the encapsulated workflow observable.
    inner_stream = MemoryStream()
    publisher = Agent(
        "publisher",
        prompt=(
            "You are a publisher. Delegate every request to the content "
            "pipeline and return its summary verbatim."
        ),
        config=config,
        tools=[
            lead.as_tool(
                description="Run the full fact-check and edit pipeline on a topic.",
                stream=inner_stream,
            )
        ],
    )

    # --- 4. Run it: the caller only ever sees task_lead_agent ---
    print("=== Nested workflow behind a single tool ===\n")
    reply = await publisher.ask(
        "Write about the discovery of penicillin by Alexander Fleming."
    )

    print("Tools the publisher saw:")
    for event in await reply.context.stream.history.get_events():
        if isinstance(event, ToolCallEvent):
            print(f"  -> {event.name}")

    # --- 5. Reveal what happened inside the encapsulated pipeline ---
    print("\nTools the encapsulated pipeline used internally:")
    for event in await inner_stream.history.get_events():
        if isinstance(event, ToolCallEvent):
            print(f"  -> {event.name}")

    print(f"\n=== Final output ===\n{reply.body}")


if __name__ == "__main__":
    asyncio.run(main())
