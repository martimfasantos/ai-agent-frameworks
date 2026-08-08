import asyncio
from workflows import Workflow, Context, step
from workflows.events import StartEvent, StopEvent
from workflows.retry_policy import (
    retry_policy,
    retry_if_exception_message,
    retry_if_exception_type,
    stop_after_attempt,
    stop_before_delay,
    wait_fixed,
    wait_random,
)


"""
-------------------------------------------------------
In this example, we explore LlamaIndex Workflows with the following features:
- Automatic retry on step failure with retry policies
- Composing a policy from primitives with retry_policy(retry=, wait=, stop=)
- Wait strategies: wait_fixed(1) + wait_random(0, 1) for jittered delays
- Stop conditions: stop_after_attempt(5) | stop_before_delay(30)
- Retry conditions: retry_if_exception_type() | retry_if_exception_message()

A step that fails might result in the entire workflow failing, but transient
errors (network timeouts, rate limits) can be safely retried. `retry_policy()`
builds a policy out of three composable primitives — when to retry, how long to
wait, and when to give up — combined with the `|` (any), `&` (all) and `+` (sum)
operators. The older ConstantDelayRetryPolicy/ExponentialBackoffRetryPolicy
classes are kept for backwards compatibility only and now emit a
DeprecationWarning.

For more details, visit:
https://developers.llamaindex.ai/python/llamaagents/workflows/retry_steps/
-------------------------------------------------------
"""


class TransientError(Exception):
    """Simulates a transient service error"""
    pass


# --- 1. A composable policy: jittered fixed delay, two stop conditions ---
class ComposedRetryWorkflow(Workflow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attempt_count = 0

    # Wait 1s plus up to 1s of jitter; give up after 5 attempts OR 30s elapsed,
    # whichever comes first.
    @step(
        retry_policy=retry_policy(
            wait=wait_fixed(1) + wait_random(0, 1),
            stop=stop_after_attempt(5) | stop_before_delay(30),
        )
    )
    async def flaky_step(self, ctx: Context, ev: StartEvent) -> StopEvent:
        """Step that fails twice, then succeeds"""
        self.attempt_count += 1
        print(f"  Attempt {self.attempt_count}...")

        if self.attempt_count < 3:
            raise TransientError(f"Transient failure on attempt {self.attempt_count}")

        return StopEvent(result=f"Succeeded after {self.attempt_count} attempts")


# --- 2. Filtering which errors are worth retrying ---
# retry_if_exception_type matches on the exception class, retry_if_exception_message
# on its string — combine them with | to retry either.
SELECTIVE_POLICY = retry_policy(
    retry=retry_if_exception_type(TransientError)
    | retry_if_exception_message(match=r".*rate limit.*"),
    wait=wait_fixed(0.5),
    stop=stop_after_attempt(3),
)


class SelectiveRetryWorkflow(Workflow):
    def __init__(self, *args, error: Exception, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = error
        self.attempt_count = 0

    @step(retry_policy=SELECTIVE_POLICY)
    async def selective_step(self, ctx: Context, ev: StartEvent) -> StopEvent:
        """Fails once with the configured error; only retried if the policy matches"""
        self.attempt_count += 1
        print(f"  Attempt {self.attempt_count}...")

        if self.attempt_count == 1:
            raise self.error

        return StopEvent(result=f"Recovered after {self.attempt_count} attempts")


# --- 3. Run all examples ---
async def main():
    print("=== Composed policy (jittered wait, two stop conditions) ===")
    w1 = ComposedRetryWorkflow(timeout=30, verbose=False)
    print(f"Result: {await w1.run()}\n")

    print("=== Selective retry: message matches 'rate limit' -> retried ===")
    w2 = SelectiveRetryWorkflow(
        timeout=30, verbose=False, error=RuntimeError("429 rate limit exceeded")
    )
    print(f"Result: {await w2.run()}\n")

    print("=== Selective retry: unmatched error -> NOT retried, workflow fails ===")
    w3 = SelectiveRetryWorkflow(
        timeout=30, verbose=False, error=ValueError("malformed input")
    )
    try:
        await w3.run()
    except ValueError as e:
        print(f"  Workflow failed as expected after 1 attempt: {e}")


if __name__ == "__main__":
    asyncio.run(main())
