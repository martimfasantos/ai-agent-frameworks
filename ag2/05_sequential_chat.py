import asyncio
import os

from ag2 import Agent
from ag2.config import OpenAIConfig
from ag2.knowledge import MemoryKnowledgeStore
from ag2.network import (
    EV_CHANNEL_CLOSED,
    EV_PACKET,
    EV_TEXT,
    WORKFLOW_TYPE,
    Hub,
    TransitionGraph,
)
from ag2.testing import TestConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- ag2.network Hub as the authoritative multi-agent coordinator
- TransitionGraph.sequence() for a deterministic agent pipeline
- Replaying the finished conversation from the hub's write-ahead log

Classic AG2's initiate_chats() sequential chat has no direct
successor in 1.0. The closest documented idiom is a workflow channel
driven by TransitionGraph.sequence(), which routes each speaker to
the next and auto-terminates after the last stage. Ordering is
deterministic and the whole transcript is recorded in the hub's WAL,
so each stage sees everything the previous ones produced.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/network/pattern_cookbook/pipeline.mdx
-------------------------------------------------------
"""

# Registered agents also get the network's peers/channels/delegate tools.
# This pipeline is pure text relay, so each stage is told to skip them.
DIRECT_REPLY = "Do not call any tools — answer directly from the transcript above. "


async def main() -> None:
    config = OpenAIConfig(model=settings.OPENAI_MODEL_NAME)

    # --- 1. Boot an in-process hub (registry + WAL + audit log) ---
    hub = await Hub.open(MemoryKnowledgeStore(), ttl_sweep_interval=0)

    # --- 2. Create the pipeline stages ---
    # The intake stage only injects the brief, so it needs no model.
    intake_agent = Agent("intake", config=TestConfig())

    researcher_agent = Agent(
        "researcher",
        prompt=(
            "You are a technology researcher. " + DIRECT_REPLY +
            "Reply on ONE line: `RESEARCH — <3 key facts, semicolon separated>`."
        ),
        config=config,
    )

    analyst_agent = Agent(
        "analyst",
        prompt=(
            "You are a business analyst. " + DIRECT_REPLY +
            "Reply on ONE line: `ANALYSIS — <2 business implications, semicolon "
            "separated>`."
        ),
        config=config,
    )

    writer_agent = Agent(
        "writer",
        prompt=(
            "You are an executive summary writer. " + DIRECT_REPLY +
            "Synthesise the research and the analysis. "
            "Reply on ONE line: `BRIEFING — <2 sentences>`."
        ),
        config=config,
    )

    # --- 3. Register every stage with the hub ---
    intake = await hub.register(intake_agent)
    researcher = await hub.register(researcher_agent)
    analyst = await hub.register(analyst_agent)
    writer = await hub.register(writer_agent)

    # --- 4. Wire the deterministic order as a TransitionGraph ---
    graph = TransitionGraph.sequence(
        [intake.agent_id, researcher.agent_id, analyst.agent_id, writer.agent_id]
    )

    channel = await intake.open(
        type=WORKFLOW_TYPE,
        target=[researcher.agent_id, analyst.agent_id, writer.agent_id],
        knobs={"graph": graph.to_dict()},
    )

    # --- 5. Send the brief and wait for the pipeline to terminate ---
    print("=== Sequential pipeline: research -> analysis -> briefing ===\n")
    await channel.send("Topic: the current state of quantum computing.")

    close_env = await intake.wait_for_channel_event(
        channel_id=channel.channel_id,
        predicate=lambda e: e.event_type == EV_CHANNEL_CLOSED,
        timeout=180.0,
    )

    # --- 6. Replay the transcript from the hub's write-ahead log ---
    names = {
        intake.agent_id: "intake",
        researcher.agent_id: "researcher",
        analyst.agent_id: "analyst",
        writer.agent_id: "writer",
    }
    for env in await hub.read_wal(channel.channel_id):
        speaker = names.get(env.sender_id, env.sender_id[:8])
        if env.event_type == EV_TEXT:
            print(f"{speaker:>12}: {env.event_data['text']}")
        elif env.event_type == EV_PACKET and env.event_data.get("body"):
            print(f"{speaker:>12}: {env.event_data['body']}")

    print(f"\n=== Pipeline closed: reason={close_env.event_data.get('reason')!r} ===")

    await hub.close()


if __name__ == "__main__":
    asyncio.run(main())
