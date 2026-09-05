import os

from pydantic import BaseModel

from agents import Agent, ModelSettings, ProgrammaticToolCallingTool, Runner
from agents.decorators import tool

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-----------------------------------------------------------------------------
In this example, we explore OpenAI's Agents SDK with the following features:
- Programmatic Tool Calling with ProgrammaticToolCallingTool
- @tool(allowed_callers=["programmatic"]) from the public agents.decorators module
- ModelSettings(tool_choice="programmatic_tool_calling")

Instead of one model round trip per tool call, the model writes a short
JavaScript program that loops, branches and combines your tools inside a
hosted V8 sandbox, then returns a single result. Here the program checks
stock for four SKUs and only fetches supplier lead times for the ones that
fall below the reorder threshold.

NOTE: Programmatic Tool Calling is Responses-API-only and needs a GPT-5.6
class model, so this example hardcodes `gpt-5.6` instead of using
`settings.OPENAI_MODEL_NAME` (gpt-4o-mini would reject the request).

For more details, visit:
https://openai.github.io/openai-agents-python/tools/
-----------------------------------------------------------------------------
"""

PROGRAMMATIC_MODEL = "gpt-5.6"

# --- 1. Simulated back-office data ---
STOCK = {"desk-lamp": 42, "office-chair": 3, "monitor": 0, "keyboard": 11}
LEAD_TIME_DAYS = {"desk-lamp": 5, "office-chair": 14, "monitor": 21, "keyboard": 7}
REORDER_THRESHOLD = 10

CALL_LOG: list[str] = []


# --- 2. Output models — programmatic tools must return an object schema ---
class Inventory(BaseModel):
    sku: str
    available_units: int


class LeadTime(BaseModel):
    sku: str
    days: int


# --- 3. Tools the generated program may call, but the model may not call directly ---
@tool(allowed_callers=["programmatic"])
def get_inventory(sku: str) -> Inventory:
    """Return the number of units currently in stock for a SKU."""
    CALL_LOG.append(f"get_inventory({sku})")
    return Inventory(sku=sku, available_units=STOCK.get(sku, 0))


@tool(allowed_callers=["programmatic"])
def get_lead_time(sku: str) -> LeadTime:
    """Return the supplier lead time in days for a SKU."""
    CALL_LOG.append(f"get_lead_time({sku})")
    return LeadTime(sku=sku, days=LEAD_TIME_DAYS.get(sku, 30))


# --- 4. Agent with exactly one ProgrammaticToolCallingTool ---
agent = Agent(
    name="Restock Planner",
    instructions=(
        "You plan restocks. Answer with one short line per SKU that needs "
        "reordering, then a single closing sentence. Be terse."
    ),
    model=PROGRAMMATIC_MODEL,
    model_settings=ModelSettings(tool_choice="programmatic_tool_calling"),
    tools=[get_inventory, get_lead_time, ProgrammaticToolCallingTool()],
)

print("=== Programmatic Tool Calling Example ===\n")

result = Runner.run_sync(
    agent,
    f"For each of {sorted(STOCK)}, check inventory. For any SKU with fewer "
    f"than {REORDER_THRESHOLD} units, also fetch its supplier lead time. "
    "Report which SKUs need reordering and how long they take to arrive.",
)

# --- 5. Show the JavaScript the model wrote and the results it returned ---
programs = 0
for response in result.raw_responses:
    for item in response.output:
        if item.type == "program":
            programs += 1
            print(f"Generated JavaScript program #{programs}:")
            print("-" * 60)
            print(item.code.rstrip())
            print("-" * 60)
        elif item.type == "program_output":
            print("Program result handed back to the model:")
            for line in item.result.splitlines():
                print(f"  {line}")
            print()

print(f"Tool calls driven by the program(s) ({len(CALL_LOG)}):")
for call in CALL_LOG:
    print(f"  - {call}")

print(f"\nAgent response:\n{result.final_output}")

print("\n=== Programmatic Tool Calling Demo Complete ===")
print(
    f"{len(CALL_LOG)} tool calls ran inside the sandbox across {programs} "
    "generated program(s) — the loop, the parallel fan-out and the threshold "
    "check cost no model round trips."
)
