import asyncio
import random
from typing import Annotated

from workflows import Workflow, Context, step
from workflows.collect import Collect, Take
from workflows.events import Event, StartEvent, StopEvent


"""
-------------------------------------------------------
In this example, we explore LlamaIndex Workflows with the following features:
- Fanning out by returning a list of events from a step (-> list[QueryEvent])
- Fanning in by accepting a list of events in a step (events: list[ResultEvent])
- Partial collection with Annotated[list[E], Collect(Take(n))]
- Declaring multiple single-event parameters to join different event types
- Running steps concurrently with num_workers
- The dynamic API: ctx.send_event() / ctx.collect_events()

Workflows run steps concurrently when a step emits several events at once.
The declarative way to do this is to return `list[SomeEvent]` (fan-out) and to
accept `list[SomeEvent]` (fan-in) — the runtime buffers the branch until every
event has arrived, so no manual bookkeeping is needed. When the number of
events is only known at runtime, the dynamic ctx.send_event()/ctx.collect_events()
API is still available.

For more details, visit:
https://developers.llamaindex.ai/python/llamaagents/workflows/concurrent_execution/
-------------------------------------------------------
"""


class QueryEvent(Event):
    query: str


class ResultEvent(Event):
    result: str


async def run_query(query: str) -> str:
    """Simulates a slow, independent unit of work"""
    delay = random.uniform(0.2, 1.0)
    await asyncio.sleep(delay)
    return f"{query} done in {delay:.1f}s"


# --- 1. Fan out with -> list[E], fan in with events: list[E] ---
class FanOutFanInWorkflow(Workflow):
    @step
    async def start(self, ev: StartEvent) -> list[QueryEvent]:
        """Returning a list fans out — one branch per event"""
        return [QueryEvent(query=f"Query {c}") for c in "ABC"]

    @step(num_workers=4)  # Run up to 4 instances of this step concurrently
    async def process(self, ev: QueryEvent) -> ResultEvent:
        return ResultEvent(result=await run_query(ev.query))

    @step
    async def collect_all(self, events: list[ResultEvent]) -> StopEvent:
        """Accepting a list fans in — this fires once, with all 3 results"""
        return StopEvent(result=[e.result for e in events])


# --- 2. Partial collection: stop as soon as N events arrive ---
class TakeFirstWorkflow(Workflow):
    @step
    async def start(self, ev: StartEvent) -> list[QueryEvent]:
        return [QueryEvent(query=f"Query {i}") for i in range(1, 4)]

    @step(num_workers=4)
    async def process(self, ev: QueryEvent) -> ResultEvent:
        return ResultEvent(result=await run_query(ev.query))

    @step
    async def first_to_finish(
        self, events: Annotated[list[ResultEvent], Collect(Take(1))]
    ) -> StopEvent:
        """Collect(Take(1)) fires on the first result instead of waiting for all"""
        return StopEvent(result=events[0].result)


# --- 3. Joining different event types with multiple parameters ---
class TaskAEvent(Event):
    query: str


class TaskBEvent(Event):
    query: str


class TaskADoneEvent(Event):
    result: str


class TaskBDoneEvent(Event):
    result: str


class MultiTypeWorkflow(Workflow):
    @step
    async def start(self, ev: StartEvent) -> list[TaskAEvent | TaskBEvent]:
        return [TaskAEvent(query="Task A"), TaskBEvent(query="Task B")]

    @step
    async def handle_a(self, ev: TaskAEvent) -> TaskADoneEvent:
        await asyncio.sleep(0.5)
        return TaskADoneEvent(result=f"{ev.query} completed")

    @step
    async def handle_b(self, ev: TaskBEvent) -> TaskBDoneEvent:
        await asyncio.sleep(0.8)
        return TaskBDoneEvent(result=f"{ev.query} completed")

    @step
    async def join(self, a: TaskADoneEvent, b: TaskBDoneEvent) -> StopEvent:
        """One parameter per event type — fires once both have arrived"""
        return StopEvent(result=f"Both done: {[a.result, b.result]}")


# --- 4. Dynamic API: when the fan-out width is only known at runtime ---
class DynamicWorkflow(Workflow):
    @step
    async def start(self, ctx: Context, ev: StartEvent) -> QueryEvent | None:
        """ctx.send_event() emits events one at a time; return None to emit nothing"""
        queries = ev.get("queries", [])
        await ctx.store.set("expected", len(queries))
        for query in queries:
            ctx.send_event(QueryEvent(query=query))
        return None

    @step(num_workers=4)
    async def process(self, ev: QueryEvent) -> ResultEvent:
        return ResultEvent(result=await run_query(ev.query))

    @step
    async def collect_all(self, ctx: Context, ev: ResultEvent) -> StopEvent | None:
        """collect_events() buffers and returns None until the quota is met"""
        expected = await ctx.store.get("expected")
        results = ctx.collect_events(ev, [ResultEvent] * expected)
        if results is None:
            return None
        return StopEvent(result=[r.result for r in results])


# --- 5. Run all workflows ---
async def main():
    print("=== Fan out / fan in with list[Event] ===")
    print(f"Result: {await FanOutFanInWorkflow(timeout=30).run()}\n")

    print("=== Partial collection with Collect(Take(1)) ===")
    print(f"Result: {await TakeFirstWorkflow(timeout=30).run()}\n")

    print("=== Joining different event types ===")
    print(f"Result: {await MultiTypeWorkflow(timeout=30).run()}\n")

    print("=== Dynamic API (runtime fan-out width) ===")
    result = await DynamicWorkflow(timeout=30).run(
        queries=["Query X", "Query Y", "Query Z", "Query W"]
    )
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
