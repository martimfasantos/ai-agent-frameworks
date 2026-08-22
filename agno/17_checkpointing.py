import os

from dotenv import load_dotenv

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.utils.pprint import pprint_run_response

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Agno with the following features:
- Checkpointing with Agent(checkpoint="tool-batch")
- Recovering a run that died mid-flight with continue_run(run_id=...)
- Branching a conversation with fork_session()

By default an agent only writes to its database at terminal states, so a
process that dies mid-run loses every tool result it had already paid for.
With checkpoint="tool-batch" the run state is written after each model turn,
so a crashed run can be resumed in place from the last checkpoint. This is
different from the paused runs in 07_human_in_the_loop.py and
16_approval_decorator.py: nothing asked for permission here, the process
simply went away.

For more details, visit:
https://docs.agno.com/examples/agents/checkpointing/crash-recovery
-------------------------------------------------------
"""

DB_FILE = "/tmp/agno_checkpointing_example.db"
SESSION_ID = "invoice-audit-session-001"

# Start from a clean database so the example is reproducible.
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)


# --- 1. Simulate a process that dies mid-run ---
class SimulatedCrash(BaseException):
    """Stands in for a SIGKILL'd worker.

    It derives from BaseException, not Exception, so Agno's tool error handling
    does not catch it and feed it back to the model — it tears the run down the
    way a real crash would.
    """


crash_armed = True

# Counts real tool invocations, to prove what the resume did NOT have to redo.
call_counts = {"list_invoices": 0, "fetch_invoice_total": 0}


# --- 2. Define expensive tools ---
@tool
def list_invoices(region: str) -> str:
    """List the invoice ids for a region.

    Args:
        region: The sales region to list invoices for.

    Returns:
        The invoice ids found for that region.
    """
    call_counts["list_invoices"] += 1
    print(f"   [tool] list_invoices({region!r}) — expensive call #{call_counts['list_invoices']}")
    return f"Invoices for {region}: INV-101, INV-102"


@tool
def fetch_invoice_total(invoice_id: str) -> str:
    """Fetch the total amount of a single invoice.

    Args:
        invoice_id: The id of the invoice to fetch.

    Returns:
        The invoice total in EUR.
    """
    call_counts["fetch_invoice_total"] += 1
    print(f"   [tool] fetch_invoice_total({invoice_id!r}) — expensive call #{call_counts['fetch_invoice_total']}")
    if crash_armed:
        raise SimulatedCrash("worker process killed while fetching invoice totals")
    totals = {"INV-101": 1200, "INV-102": 1200}
    return f"{invoice_id} total: {totals.get(invoice_id, 0)} EUR"


# --- 3. Create the agent with checkpointing enabled ---
agent = Agent(
    model=OpenAIChat(id=settings.OPENAI_MODEL_NAME),
    db=SqliteDb(db_file=DB_FILE),
    checkpoint="tool-batch",
    tools=[list_invoices, fetch_invoice_total],
    add_history_to_context=True,
    num_history_runs=5,
    instructions=[
        "First list the invoices for the region, then fetch the total of every invoice id you found.",
        "Answer in one plain sentence. No bullet lists, no formulas.",
    ],
    markdown=True,
)

# --- 4. The run crashes after the first tool batch ---
print("=== Step 1: Run crashes mid-flight ===\n")
try:
    agent.run("What is the combined invoice total for Iberia?", session_id=SESSION_ID)
except SimulatedCrash as error:
    print(f"\n💥 Process died: {error}")

# --- 5. Inspect what survived in the database ---
print("\n=== Step 2: What the checkpoint saved ===\n")
crashed_run = agent.get_last_run_output(session_id=SESSION_ID)
print(f"Run id:      {crashed_run.run_id}")
print(f"Run status:  {crashed_run.status}  (never reached a terminal state)")
print("Tool results already persisted:")
for tool_execution in crashed_run.tools or []:
    print(f"  - {tool_execution.tool_name}: {tool_execution.result}")

# --- 6. Resume the crashed run in place ---
# Same run_id: the agent picks up from the checkpoint instead of starting over.
print("\n=== Step 3: Resume the crashed run ===\n")
crash_armed = False
resumed_output = agent.continue_run(run_id=crashed_run.run_id, session_id=SESSION_ID)
pprint_run_response(resumed_output)

print(f"\nRun status: {resumed_output.status}")
print(f"list_invoices calls (whole example): {call_counts['list_invoices']}")
print("  -> the resume replayed the checkpointed result instead of calling it again")

# --- 7. Branch the finished conversation into a new session ---
# fork_session deep-copies every run into a fresh session_id, so an alternative
# follow-up can be explored without polluting the audited original.
print("\n=== Step 4: Fork the session to explore a branch ===\n")
forked_session_id = agent.fork_session(source_session_id=SESSION_ID)
print(f"Forked '{SESSION_ID}' -> '{forked_session_id}'\n")

calls_before_branch = call_counts["fetch_invoice_total"]

branch_output = agent.run(
    "Using only the totals you already fetched, what is the average invoice amount?",
    session_id=forked_session_id,
)
pprint_run_response(branch_output)

original_runs = len(agent.get_session(session_id=SESSION_ID).runs or [])
forked_runs = len(agent.get_session(session_id=forked_session_id).runs or [])
print(f"\nRuns in original session: {original_runs} (untouched)")
print(f"Runs in forked session:   {forked_runs} (inherited history + the branch)")
print(
    f"fetch_invoice_total calls: {calls_before_branch} before the fork, "
    f"{call_counts['fetch_invoice_total']} after the branch"
)
print("  -> the branch answered from the forked history, no tool re-run")
