import asyncio

from workflows import Workflow, Context, catch_error, step
from workflows.events import Event, StartEvent, StepFailedEvent, StopEvent
from workflows.retry_policy import retry_policy, stop_after_attempt, wait_fixed


"""
-------------------------------------------------------
In this example, we explore LlamaIndex Workflows with the following features:
- @catch_error to handle a step that has exhausted its retries
- for_steps=[...] to scope a handler to specific steps
- A bare @catch_error as a catch-all for every step
- max_recoveries to cap how often a handler may rescue the same step
- StepFailedEvent (.step_name, .exception, .attempts) as a normal event
- Context.retry_info() to inspect retry_number and last_exception

Retry policies decide whether to run a step again; error recovery decides what
happens once retrying is over. A @catch_error handler receives a StepFailedEvent
and returns an ordinary event, so a failure becomes just another branch of the
workflow — serve stale data, fall back to a cheaper provider, or stop cleanly.
`.exception` is a live Python exception, not a string, so it can be re-raised or
matched on with isinstance.

For more details, visit:
https://developers.llamaindex.ai/python/llamaagents/workflows/retry_steps/
-------------------------------------------------------
"""


class DataEvent(Event):
    payload: str
    from_cache: bool


class RetryFetchEvent(Event):
    reason: str


# --- 1. Scoped recovery: rescue one named step after its retries run out ---
class CachedFallbackWorkflow(Workflow):
    @step(retry_policy=retry_policy(wait=wait_fixed(0.2), stop=stop_after_attempt(2)))
    async def fetch(self, ctx: Context, ev: StartEvent) -> DataEvent:
        """Always fails, so the retry policy is exhausted and recovery kicks in"""
        info = ctx.retry_info()
        print(
            f"  fetch: retry_number={info.retry_number} "
            f"last_exception={info.last_exception!r}"
        )
        raise ConnectionError("upstream API is down")

    # for_steps scopes this handler; max_recoveries caps how many times it may
    # rescue that step within a single run.
    @catch_error(for_steps=["fetch"], max_recoveries=2)
    async def serve_stale(self, ctx: Context, ev: StepFailedEvent) -> DataEvent:
        print(
            f"  recovery: {ev.step_name} failed after {ev.attempts} attempts "
            f"with {type(ev.exception).__name__}: {ev.exception}"
        )
        return DataEvent(payload="yesterday's prices", from_cache=True)

    @step
    async def report(self, ev: DataEvent) -> StopEvent:
        source = "cache" if ev.from_cache else "upstream"
        return StopEvent(result=f"{ev.payload} (from {source})")


# --- 2. Catch-all recovery, and what happens once max_recoveries is spent ---
class RecoveryBudgetWorkflow(Workflow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attempts = 0

    @step
    async def unstable(self, ev: StartEvent | RetryFetchEvent) -> DataEvent:
        """Fails every time — the recovery budget decides when to stop trying"""
        self.attempts += 1
        print(f"  unstable: call {self.attempts}")
        raise TimeoutError("provider timed out")

    # A bare @catch_error handles failures from any step. This one loops the
    # workflow back into `unstable`, so it burns a recovery each time; once the
    # budget is spent the failure propagates and the run fails.
    @catch_error(max_recoveries=2)
    async def retry_elsewhere(self, ctx: Context, ev: StepFailedEvent) -> RetryFetchEvent:
        print(f"  recovery: retrying after {type(ev.exception).__name__}")
        return RetryFetchEvent(reason=str(ev.exception))

    @step
    async def report(self, ev: DataEvent) -> StopEvent:
        return StopEvent(result=ev.payload)


# --- 3. Run both workflows ---
async def main():
    print("=== Scoped recovery: fall back to cached data ===")
    result = await CachedFallbackWorkflow(timeout=30).run()
    print(f"Result: {result}\n")

    print("=== Catch-all recovery with a spent budget ===")
    try:
        await RecoveryBudgetWorkflow(timeout=30).run()
    except TimeoutError as e:
        print(f"  Workflow failed once max_recoveries was exhausted: {e}")


if __name__ == "__main__":
    asyncio.run(main())
