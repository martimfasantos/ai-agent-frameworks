import os

from pydantic import BaseModel, Field

from crewai import Agent, Crew, Task
from crewai.events import BaseEventListener, ToolFailureDetectedEvent
from crewai.tools import (
    BaseTool,
    ToolExecutionFailedError,
    ToolFailure,
    ToolFailurePolicy,
    ToolFailureReason,
)

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI with the following features:
- Returning a ToolFailure from BaseTool._run instead of an error string
- ToolFailurePolicy.IGNORE / WARN / RAISE and its precedence order
- result.has_tool_failures and result.tool_failures on the crew output
- The ToolFailureDetectedEvent on the event bus

A tool can finish without raising and still have failed - an API answering
HTTP 200 with {"ok": false}, an MCP server setting isError. Such a call used to
reach the agent as ordinary text and the run was recorded as a success.
Returning a ToolFailure declares the failure: the agent still reads the message,
but the framework records it, emits an event and - under RAISE - aborts. The
effective policy is resolved most-specific-first: tool, task, agent, crew, then
WARN.

For more details, visit:
https://docs.crewai.com/en/concepts/tools
-------------------------------------------------------
"""


# --- 1. A tool that declares failure instead of returning an error string ---
class InventoryInput(BaseModel):
    sku: str = Field(description="The stock keeping unit to look up.")


class CheckInventoryTool(BaseTool):
    name: str = "check_inventory"
    description: str = "Checks warehouse stock for a SKU."
    args_schema: type[BaseModel] = InventoryInput

    def _run(self, sku: str) -> str | ToolFailure:
        if sku == "SKU-1":
            return "SKU-1: 42 units in stock"
        return ToolFailure(
            message=f"SKU '{sku}' is not in the warehouse catalog",
            reason=ToolFailureReason.TOOL_REPORTED,
            code="sku_not_found",
            retryable=False,
            details={"catalog_size": 1},
        )


# --- 2. Watch the event bus for declared failures ---
class FailureWatcher(BaseEventListener):
    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(ToolFailureDetectedEvent)
        def on_tool_failure(source, event):
            print(
                f"[EVENT] ToolFailureDetectedEvent tool={event.tool_name} "
                f"code={event.failure.code} policy={event.policy.value}"
            )


watcher = FailureWatcher()


def build_agent(tool: CheckInventoryTool) -> Agent:
    return Agent(
        role="Inventory Clerk",
        goal="Answer stock questions using the inventory tool",
        backstory=(
            "You look a SKU up exactly once. If the tool reports the SKU is not "
            "in the catalog, you stop and say so in one sentence."
        ),
        tools=[tool],
        llm=settings.OPENAI_MODEL_NAME,
        max_iter=3,
    )


def build_task(agent: Agent) -> Task:
    return Task(
        description="How many units of SKU-9 are in stock?",
        expected_output="One sentence with the stock level, or why it is unknown.",
        agent=agent,
    )


# --- 3. Default policy (WARN): record the failure and keep going ---
print("=== 1. Default policy (WARN) ===")

warn_agent = build_agent(CheckInventoryTool())
warn_crew = Crew(agents=[warn_agent], tasks=[build_task(warn_agent)])
result = warn_crew.kickoff()

print(f"\nAnswer: {result.raw}")
print(f"has_tool_failures: {result.has_tool_failures}")
for record in result.tool_failures:
    print(
        f"  tool={record.tool_name} code={record.failure.code} "
        f"reason={record.failure.reason.value} retryable={record.failure.retryable} "
        f"agent={record.agent_role}"
    )
    print(f"  args={record.tool_args} message={record.message}")

# --- 4. Precedence: the tool's RAISE beats the crew's IGNORE ---
print("\n=== 2. Precedence (tool RAISE over crew IGNORE) ===")

raise_agent = build_agent(CheckInventoryTool(tool_failure_policy=ToolFailurePolicy.RAISE))
raise_crew = Crew(
    agents=[raise_agent],
    tasks=[build_task(raise_agent)],
    tool_failure_policy=ToolFailurePolicy.IGNORE,
)

try:
    raise_crew.kickoff()
except ToolExecutionFailedError as failed:
    print(f"kickoff() aborted: {failed.record.summary()}")
