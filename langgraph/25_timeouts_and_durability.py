import asyncio

from dotenv import load_dotenv

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import NodeTimeoutError
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy, TimeoutPolicy
from typing_extensions import TypedDict

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore LangGraph with the following features:
- Per-node wall-clock timeouts with add_node(..., timeout=seconds)
- TimeoutPolicy(run_timeout=..., idle_timeout=...) for finer control
- Catching NodeTimeoutError, and combining a timeout with a RetryPolicy
- The async-only constraint: timeout= on a sync node fails at compile time
- Checkpoint durability modes: durability="sync" / "async" / "exit"

Timeouts bound how long a single node attempt may run; the resulting
NodeTimeoutError then flows into the node's retry policy, so a flaky
dependency can be capped and retried rather than hanging the graph.
Durability controls how often the checkpointer is written: "sync" and
"async" persist every super-step (resumable mid-run), while "exit" writes
only once at the end (fastest, but a crash loses the whole run).

For more details, visit:
https://docs.langchain.com/oss/python/langgraph/fault-tolerance#timeouts
-----------------------------------------------------------------------
"""


class State(TypedDict, total=False):
    label: str
    attempts: int
    result: str


# --- 1. Timeouts are async-only — a sync node raises at compile time ---
print("=== Constraint: timeout= requires an async node ===\n")


def sync_node(state: State) -> dict:
    return {"result": "done"}


sync_builder = StateGraph(State)
sync_builder.add_node("sync_node", sync_node, timeout=1.0)  # accepted here...
sync_builder.add_edge(START, "sync_node")
sync_builder.add_edge("sync_node", END)
try:
    sync_builder.compile()  # ...and rejected here
except ValueError as exc:
    print(f"  ValueError at compile(): {exc}\n")


# --- 2. An async node that overruns its timeout ---
async def slow_fetch(state: State) -> dict:
    """Simulate a dependency that takes longer than we are willing to wait."""
    await asyncio.sleep(2.0)
    return {"result": "fetched"}


timeout_builder = StateGraph(State)
timeout_builder.add_node("slow_fetch", slow_fetch, timeout=0.3)
timeout_builder.add_edge(START, "slow_fetch")
timeout_builder.add_edge("slow_fetch", END)
timeout_graph = timeout_builder.compile()


# --- 3. A timeout with a retry policy: the second attempt is fast enough ---
attempts = {"count": 0}


async def flaky_fetch(state: State) -> dict:
    """First attempt overruns the timeout, later attempts return immediately."""
    attempts["count"] += 1
    if attempts["count"] == 1:
        await asyncio.sleep(2.0)
    return {
        "result": f"fetched on attempt {attempts['count']}",
        "attempts": attempts["count"],
    }


retry_builder = StateGraph(State)
retry_builder.add_node(
    "flaky_fetch",
    flaky_fetch,
    timeout=TimeoutPolicy(run_timeout=0.3, idle_timeout=0.2),
    retry_policy=RetryPolicy(max_attempts=3, retry_on=(NodeTimeoutError,)),
)
retry_builder.add_edge(START, "flaky_fetch")
retry_builder.add_edge("flaky_fetch", END)
retry_graph = retry_builder.compile()


# --- 4. Durability modes: count the checkpoints each one leaves behind ---
def step(state: State) -> dict:
    return {"attempts": state.get("attempts", 0) + 1}


durability_builder = StateGraph(State)
durability_builder.add_node("first", step)
durability_builder.add_node("second", step)
durability_builder.add_node("third", step)
durability_builder.add_edge(START, "first")
durability_builder.add_edge("first", "second")
durability_builder.add_edge("second", "third")
durability_builder.add_edge("third", END)


async def main() -> None:
    print("=== Async node exceeding timeout=0.3 ===\n")
    try:
        await timeout_graph.ainvoke({"label": "slow"})
    except NodeTimeoutError as exc:
        print(f"  NodeTimeoutError: {exc}\n")

    print("=== TimeoutPolicy + RetryPolicy(retry_on=NodeTimeoutError) ===\n")
    policy = TimeoutPolicy(run_timeout=0.3, idle_timeout=0.2)
    print(f"  run_timeout={policy.run_timeout}s  idle_timeout={policy.idle_timeout}s")
    result = await retry_graph.ainvoke({"label": "flaky"})
    print(f"  attempt 1 timed out, then: {result['result']}\n")

    print("=== Durability modes over a 3-node run ===\n")
    for mode in ("sync", "async", "exit"):
        graph = durability_builder.compile(checkpointer=InMemorySaver())
        config = {"configurable": {"thread_id": f"thread-{mode}"}}
        async for _ in graph.astream({"attempts": 0}, config=config, durability=mode):
            pass
        history = [snapshot async for snapshot in graph.aget_state_history(config)]
        print(f"  durability={mode:<6} -> {len(history)} checkpoint(s) persisted")
    print()
    print('  "sync"/"async" write every super-step, so the run is resumable from')
    print('  the last completed node. "exit" writes once at the end — cheapest,')
    print("  but an interrupted run has nothing to resume from.")


if __name__ == "__main__":
    asyncio.run(main())
