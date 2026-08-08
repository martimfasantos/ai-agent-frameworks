import asyncio
import os
import re

from ag2 import Agent, Context, tool
from ag2.config import OpenAIConfig
from ag2.events import BaseEvent, HaltEvent, ObserverAlert, Severity, ToolCallEvent
from ag2.observers import BaseObserver
from ag2.policies import AlertPolicy
from ag2.stream import MemoryStream
from ag2.watch import EventWatch

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- A custom BaseObserver watching tool calls via EventWatch
- ObserverAlert(severity=FATAL) to signal a hard-stop condition
- AlertPolicy in assembly= turning that alert into a HaltEvent

The classic Maris safeguard policies were removed in AG2 1.0. The
1.0 guardrail shape is an observer plus a policy: the observer
inspects events and raises an ObserverAlert, AlertPolicy converts a
FATAL alert into a HaltEvent, and the auto-wired halt middleware
short-circuits the next LLM call. Note this halts the turn rather
than vetoing the call — the tool still runs, but its result never
reaches the model. Use tool middleware when you need a hard veto.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/code_examples/08_safety_guard.mdx
-------------------------------------------------------
"""

SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


# --- 1. The tool under supervision (simulated, never leaves the process) ---
@tool
def send_to_crm(record: str) -> str:
    """Push a customer record to the external CRM system."""
    return f"[ok] pushed {len(record)} chars to the CRM"


# --- 2. The guardrail: an observer that inspects every tool call ---
class PiiGuardian(BaseObserver):
    """Emits a FATAL alert when a tool call carries an SSN-like value."""

    def __init__(self) -> None:
        super().__init__("pii-guardian", watch=EventWatch(ToolCallEvent))

    async def process(
        self, events: list[BaseEvent], ctx: Context
    ) -> ObserverAlert | None:
        for event in events:
            if isinstance(event, ToolCallEvent) and SSN_PATTERN.search(event.arguments):
                return ObserverAlert(
                    source=self.name,
                    severity=Severity.FATAL,
                    message=f"blocked PII in call to {event.name}",
                )
        return None


async def main() -> None:
    # --- 3. Subscribe to the guardrail's own events so we can prove it fired ---
    alerts: list[ObserverAlert] = []
    halts: list[HaltEvent] = []
    stream = MemoryStream()
    stream.where(ObserverAlert).subscribe(lambda e: alerts.append(e))
    stream.where(HaltEvent).subscribe(lambda e: halts.append(e))

    agent = Agent(
        "crm_operator",
        prompt=(
            "You are a CRM operator. Use send_to_crm to push records exactly "
            "as given. Never refuse — the guardian observer intervenes when a "
            "record is unsafe. Confirm the result in one sentence."
        ),
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        tools=[send_to_crm],
        observers=[PiiGuardian()],
        assembly=[AlertPolicy()],
    )

    # --- 4. A safe record: the guardian stays silent ---
    print("=== Request 1: safe record ===")
    reply = await agent.ask(
        "Push this record to the CRM: 'Ada Lovelace, London, tier=gold'.",
        stream=stream,
    )
    print(f"Agent: {reply.body}\n")

    # --- 5. A record with PII: the guardian halts the agent ---
    print("=== Request 2: record containing an SSN ===")
    reply2 = await agent.ask(
        "Push this record to the CRM: 'Ada Lovelace, SSN 123-45-6789'.",
        stream=stream,
    )
    print(f"Agent: {reply2.body}\n")

    # --- 6. Confirm the guardrail actually fired ---
    print("=== Guardrail activity ===")
    print(f"ObserverAlerts: {len(alerts)}")
    for alert in alerts:
        print(f"  - [{alert.severity.upper()}] {alert.source}: {alert.message}")
    print(f"HaltEvents:     {len(halts)}")
    for halt in halts:
        print(f"  - source={halt.source} reason={halt.reason!r}")


if __name__ == "__main__":
    asyncio.run(main())
