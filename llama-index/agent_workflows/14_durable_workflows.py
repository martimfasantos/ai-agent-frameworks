import asyncio
import json
from typing import Annotated

from workflows import Workflow, Context, step
from workflows.events import Event, StartEvent, StepState, StepStateChanged, StopEvent
from workflows.resource import Resource


"""
-------------------------------------------------------
In this example, we explore LlamaIndex Workflows with the following features:
- Snapshotting a running workflow with handler.ctx.to_dict()
- Watching internal events via handler.stream_events(expose_internal=True)
- StepStateChanged / StepState.NOT_RUNNING as a safe point to snapshot
- Resuming from a snapshot with Context.from_dict() and wf.run(ctx=ctx)
- Keeping heavy dependencies in a Resource so they stay out of the snapshot

A long workflow should survive the process that started it. Because a Context is
serialisable, a run can be snapshotted to JSON after any step, stored anywhere,
and resumed later — possibly on a different machine. Snapshot on
StepStateChanged with StepState.NOT_RUNNING, which fires when a step has
finished and nothing is mid-flight, so the snapshot is consistent. Anything
expensive or unpicklable (a DB pool, an LLM client) belongs in a Resource:
resources are rebuilt by their factory on resume instead of being serialised.

For more details, visit:
https://developers.llamaindex.ai/python/llamaagents/workflows/durable_workflows/
-------------------------------------------------------
"""


class ChunkEvent(Event):
    index: int


# --- 1. A heavy dependency that must NOT end up in the snapshot ---
class EmbeddingClient:
    """Stands in for a real client holding sockets, pools or model weights"""

    def __init__(self):
        print("  [resource] EmbeddingClient built")

    def embed(self, index: int) -> float:
        return round(index * 0.5, 2)


def get_embedding_client() -> EmbeddingClient:
    return EmbeddingClient()


# --- 2. A workflow that accumulates state across several steps ---
class IndexingWorkflow(Workflow):
    @step
    async def start(self, ctx: Context, ev: StartEvent) -> ChunkEvent:
        await ctx.store.set("embeddings", [])
        return ChunkEvent(index=0)

    @step
    async def process_chunk(
        self,
        ctx: Context,
        ev: ChunkEvent,
        client: Annotated[EmbeddingClient, Resource(get_embedding_client)],
    ) -> ChunkEvent | StopEvent:
        """Embed one chunk per step so there are snapshot points in between"""
        embeddings = await ctx.store.get("embeddings")
        embeddings.append(client.embed(ev.index))
        await ctx.store.set("embeddings", embeddings)
        print(f"  processed chunk {ev.index} -> {embeddings}")

        if ev.index < 3:
            return ChunkEvent(index=ev.index + 1)
        return StopEvent(result=embeddings)


# --- 3. Run, snapshot mid-flight, then abandon the run ---
async def snapshot_after_two_chunks(workflow: IndexingWorkflow) -> dict:
    handler = workflow.run()
    processed = 0

    # expose_internal=True adds the runtime's own events to the stream
    async for event in handler.stream_events(expose_internal=True):
        if (
            isinstance(event, StepStateChanged)
            and event.name == "process_chunk"
            and event.step_state == StepState.NOT_RUNNING
        ):
            processed += 1
            if processed == 2:
                snapshot = handler.ctx.to_dict()
                await handler.cancel_run()
                print("  snapshot taken, run cancelled")
                return snapshot

    raise RuntimeError("workflow finished before a snapshot could be taken")


# --- 4. Resume from the snapshot in a fresh Context ---
async def main():
    workflow = IndexingWorkflow(timeout=60)

    print("=== First process: run until two chunks are done ===")
    snapshot = await snapshot_after_two_chunks(workflow)

    # The snapshot is plain JSON, so it can go to a file, Redis or a database
    stored = json.dumps(snapshot)
    print(f"\nSnapshot is {len(stored)} bytes of JSON")
    print(f"Top-level keys: {sorted(snapshot)}")
    captured = snapshot["state"]["state_data"]["_data"]["embeddings"]
    print(f"Captured embeddings: {captured}")
    print(f"EmbeddingClient in snapshot? {'EmbeddingClient' in stored}")

    print("\n=== Second process: restore and finish the job ===")
    restored_ctx = Context.from_dict(workflow, json.loads(stored))
    result = await workflow.run(ctx=restored_ctx)
    print(f"Result: {result}")

    # Two things worth noting above: the EmbeddingClient never appears in the
    # snapshot (the Resource factory supplies it on each run instead), and chunk 2
    # is processed twice because the snapshot predates its result being recorded.
    # Snapshot/resume is at-least-once, so steps should be idempotent.


if __name__ == "__main__":
    asyncio.run(main())
