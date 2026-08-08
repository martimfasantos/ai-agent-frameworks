import asyncio

from workflows import Workflow, Context, step
from workflows.events import (
    Event,
    StartEvent,
    StepStateChanged,
    StopEvent,
)
from workflows.testing import WorkflowTestRunner


"""
-------------------------------------------------------
In this example, we explore LlamaIndex Workflows with the following features:
- WorkflowTestRunner for running a workflow end-to-end in a test
- Asserting on result.result, .collected and .event_types
- expose_internal to include or hide the runtime's own events
- exclude_events to drop noisy event types from the collection
- Reusing result.ctx to assert on the state a run left behind
- A snapshot/restore round-trip driven entirely through the test runner

Workflows are event-driven, so asserting only on the final result misses most of
what a workflow does. WorkflowTestRunner runs the workflow, collects everything
that crossed the event stream, and hands back the Context, so a test can assert
that the right steps fired the right number of times and that state ended up
where it should. It needs no test framework — these are plain asserts.

For more details, visit:
https://developers.llamaindex.ai/python/llamaagents/workflows/testing/
-------------------------------------------------------
"""


class GreetEvent(Event):
    name: str


class ProgressEvent(Event):
    message: str


class NamedStartEvent(StartEvent):
    """Custom start event — steps must annotate it explicitly, since routing on
    event subclasses is opt-in (@step(accept_event_subclasses=True))."""
    name: str


# --- 1. The workflow under test ---
class GreetingWorkflow(Workflow):
    @step
    async def start(self, ctx: Context, ev: NamedStartEvent) -> GreetEvent:
        return GreetEvent(name=ev.name)

    @step
    async def greet(self, ctx: Context, ev: GreetEvent) -> StopEvent:
        ctx.write_event_to_stream(ProgressEvent(message=f"greeting {ev.name}"))
        greeted = await ctx.store.get("greeted", default=[])
        greeted.append(ev.name)
        await ctx.store.set("greeted", greeted)
        return StopEvent(result=f"Hello, {ev.name}!")


# --- 2. Assert on the result, the events and the leftover state ---
async def test_full_run() -> None:
    result = await WorkflowTestRunner(GreetingWorkflow(timeout=30)).run(
        start_event=NamedStartEvent(name="Ada"),
    )

    assert str(result.result) == "Hello, Ada!"

    # Every step transition is visible because expose_internal defaults to True
    assert result.event_types[StepStateChanged] > 0
    assert result.event_types[ProgressEvent] == 1

    # The Context survives the run, so state can be asserted on directly
    assert await result.ctx.store.get("greeted") == ["Ada"]

    print(f"  result: {result.result}")
    print(f"  {len(result.collected)} events collected")
    for event_type, count in sorted(
        result.event_types.items(), key=lambda kv: kv[0].__name__
    ):
        print(f"    {event_type.__name__}: {count}")


# --- 3. Hide the runtime noise to assert only on your own events ---
async def test_only_user_events() -> None:
    result = await WorkflowTestRunner(GreetingWorkflow(timeout=30)).run(
        start_event=NamedStartEvent(name="Grace"),
        expose_internal=False,
        exclude_events=[StepStateChanged],
    )

    assert StepStateChanged not in result.event_types
    assert [type(e).__name__ for e in result.collected] == [
        "ProgressEvent",
        "StopEvent",
    ]

    print(f"  collected: {[type(e).__name__ for e in result.collected]}")


# --- 4. Round-trip the Context through a snapshot and keep running ---
async def test_snapshot_restore() -> None:
    workflow = GreetingWorkflow(timeout=30)

    first = await WorkflowTestRunner(workflow).run(
        start_event=NamedStartEvent(name="Alan"),
    )
    snapshot = first.ctx.to_dict()

    # A restored Context carries the earlier state into the next run
    restored = Context.from_dict(workflow, snapshot)
    assert await restored.store.get("greeted") == ["Alan"]

    second = await WorkflowTestRunner(workflow).run(
        start_event=NamedStartEvent(name="Ada"),
        ctx=restored,
    )
    assert str(second.result) == "Hello, Ada!"
    assert await second.ctx.store.get("greeted") == ["Alan", "Ada"]

    print(f"  state after snapshot round-trip: {await second.ctx.store.get('greeted')}")


# --- 5. Run the tests ---
async def main():
    for test in (test_full_run, test_only_user_events, test_snapshot_restore):
        print(f"=== {test.__name__} ===")
        await test()
        print("  PASSED\n")


if __name__ == "__main__":
    asyncio.run(main())
