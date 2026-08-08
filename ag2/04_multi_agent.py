import asyncio
import os

from ag2 import Agent
from ag2.config import OpenAIConfig
from ag2.events import ToolCallEvent

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- Multi-agent collaboration via Agent.as_tool() subagents
- LLM-driven orchestration: the coordinator picks who works next
- Sharing findings between agents through the context parameter

AG2 1.0 replaces classic group chat with subagents: each
specialist becomes a task_<name> tool on the coordinator, and the
coordinator's model decides which to call and in what order. This
is the direct successor to AutoPattern's LLM-based speaker
selection, with each sub-task running on its own isolated stream.

For more details, visit:
https://docs.ag2.ai/latest/docs/beta/subagents/
-------------------------------------------------------
"""


async def main() -> None:
    config = OpenAIConfig(model=settings.OPENAI_MODEL_NAME)

    # --- 1. Create the specialist agents ---
    researcher = Agent(
        "researcher",
        prompt=(
            "You are a research specialist. Present key facts about the topic "
            "as 3-4 short bullet points. Facts only, no prose."
        ),
        config=config,
    )

    writer = Agent(
        "writer",
        prompt=(
            "You are a content writer. Turn the research notes you are given "
            "into one engaging paragraph of 3-4 sentences."
        ),
        config=config,
    )

    critic = Agent(
        "critic",
        prompt=(
            "You are a quality reviewer. Judge the draft for accuracy and "
            "clarity in 1-2 sentences, or reply 'Approved' if it is good."
        ),
        config=config,
    )

    # --- 2. Expose each specialist to the coordinator as a tool ---
    coordinator = Agent(
        "coordinator",
        prompt=(
            "You coordinate a writing team. First delegate research, then pass "
            "the findings to the writer via the context parameter, then send the "
            "draft to the critic. Finish by printing the approved paragraph."
        ),
        config=config,
        tools=[
            researcher.as_tool(description="Research a topic and return key facts."),
            writer.as_tool(
                description="Write a paragraph. Pass research notes in the context parameter."
            ),
            critic.as_tool(
                description="Review a draft. Pass the draft in the context parameter."
            ),
        ],
    )

    # --- 3. Run the collaboration ---
    print("=== Multi-agent collaboration via subagents ===\n")
    reply = await coordinator.ask(
        "Write a short piece about the history of the Python programming language."
    )

    # --- 4. Show which specialists the coordinator actually used ---
    print("Delegations the coordinator's model chose:")
    for event in await reply.context.stream.history.get_events():
        if isinstance(event, ToolCallEvent):
            print(f"  -> {event.name}")

    print(f"\n=== Final output ===\n{reply.body}")


if __name__ == "__main__":
    asyncio.run(main())
