import asyncio
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from agent_framework import (
    CheckpointStorage,
    Executor,
    InMemoryCheckpointStorage,
    Workflow,
    WorkflowBuilder,
    WorkflowCheckpoint,
    WorkflowContext,
    handler,
)

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Microsoft Agent Framework
with the following features:
- WorkflowBuilder(checkpoint_storage=...) to persist progress
- on_checkpoint_save / on_checkpoint_restore executor hooks
- checkpoint_storage.get_latest(workflow_name=...) to find where to resume
- workflow.run(checkpoint_id=...) to replay a failed run

A checkpointed workflow snapshots its queued messages and its
executors' internal state at the end of every superstep, so a crash
costs at most one superstep of work. Here an executor throws mid-run,
then we rebuild the graph from scratch with empty executors and resume
from the last checkpoint — the already-computed results come back with
it. This example makes no LLM calls at all.

For more details, visit:
https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints?pivots=programming-language-python
-------------------------------------------------------
"""

WORKFLOW_NAME = "divisor-scan"
UPPER_LIMIT = 8


# --- 1. Define the message type carried between supersteps ---
@dataclass
class ComputeTask:
    remaining: list[int]


# --- 2. A start executor that seeds the work queue ---
class StartExecutor(Executor):
    """Turns an upper limit into the list of numbers still to process."""

    @handler
    async def start(self, upper_limit: int, ctx: WorkflowContext[ComputeTask]) -> None:
        print(f"[start] queueing numbers 1..{upper_limit}")
        await ctx.send_message(ComputeTask(remaining=list(range(1, upper_limit + 1))))


# --- 3. A worker that self-loops and checkpoints its accumulated state ---
class WorkerExecutor(Executor):
    """Computes divisors one number per superstep, accumulating results."""

    def __init__(self, id: str, fail_on: int | None = None) -> None:
        super().__init__(id=id)
        self._fail_on = fail_on  # simulates a transient fault on one number
        self._divisors: dict[int, list[int]] = {}

    @handler
    async def compute(
        self, task: ComputeTask, ctx: WorkflowContext[ComputeTask, dict[int, list[int]]]
    ) -> None:
        number = task.remaining.pop(0)
        if number == self._fail_on:
            raise RuntimeError(f"transient fault while processing {number}")

        self._divisors[number] = [i for i in range(1, number + 1) if number % i == 0]
        print(f"[worker] divisors of {number}: {self._divisors[number]}")

        if task.remaining:
            await ctx.send_message(task)  # self-loop: one number per superstep
        else:
            await ctx.yield_output(self._divisors)

    # These two hooks are what carry executor state across a crash.
    async def on_checkpoint_save(self) -> dict[str, Any]:
        return {"divisors": self._divisors}

    async def on_checkpoint_restore(self, state: dict[str, Any]) -> None:
        self._divisors = state.get("divisors", {})
        print(f"[worker] restored {len(self._divisors)} result(s) from checkpoint")


# --- 4. Build a workflow with checkpoint storage attached ---
def build_workflow(
    checkpoint_storage: CheckpointStorage, fail_on: int | None = None
) -> Workflow:
    """Builds a fresh graph with empty executors, sharing one checkpoint store."""
    start = StartExecutor(id="start")
    worker = WorkerExecutor(id="worker", fail_on=fail_on)
    return (
        WorkflowBuilder(
            name=WORKFLOW_NAME,
            start_executor=start,
            checkpoint_storage=checkpoint_storage,
        )
        .add_edge(start, worker)
        .add_edge(worker, worker)
        .build()
    )


async def main() -> None:
    checkpoint_storage = InMemoryCheckpointStorage()

    # --------------------------------------------------------------
    # Example 1: A run that dies part-way through
    # --------------------------------------------------------------
    print("=== Example 1: Run until an executor throws ===")
    workflow = build_workflow(checkpoint_storage, fail_on=3)

    supersteps = 0
    try:
        async for event in workflow.run(message=UPPER_LIMIT, stream=True):
            if event.type == "superstep_completed":
                supersteps += 1  # one checkpoint is written per superstep
    except RuntimeError as exc:
        print(f"[crash] {exc} — in-memory state is gone")

    # --- 5. Locate the checkpoint written at the end of the last superstep ---
    latest: WorkflowCheckpoint | None = await checkpoint_storage.get_latest(
        workflow_name=WORKFLOW_NAME
    )
    assert latest is not None, "checkpointing produced no snapshot"
    print(f"\nSupersteps completed: {supersteps}")
    print(f"Latest checkpoint:    {latest.checkpoint_id}")
    print(f"Iteration count:      {latest.iteration_count}")
    print(f"Queued messages:      {len(latest.messages)}")

    # --------------------------------------------------------------
    # Example 2: Resume from that checkpoint in a brand-new workflow
    # --------------------------------------------------------------
    print("\n=== Example 2: Resume from the checkpoint ===")
    resumed = build_workflow(checkpoint_storage)  # no fault, executors start empty

    divisors: dict[int, list[int]] | None = None
    async for event in resumed.run(checkpoint_id=latest.checkpoint_id, stream=True):
        if event.type == "output":
            divisors = event.data

    # --- 6. Show that pre-crash work survived the replay ---
    assert divisors is not None, "resumed workflow produced no output"
    print(f"\nCompleted numbers: {sorted(divisors)}")
    print(f"Perfect numbers:   {[n for n, d in divisors.items() if sum(d) == 2 * n]}")
    print(
        f"All {UPPER_LIMIT} numbers present after resume: "
        f"{sorted(divisors) == list(range(1, UPPER_LIMIT + 1))}"
    )


if __name__ == "__main__":
    asyncio.run(main())
