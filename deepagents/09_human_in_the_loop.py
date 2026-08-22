from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from deepagents import create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Human-in-the-loop approval via the interrupt_on= parameter
- Pausing the run before a sensitive tool call fires
- Resuming with an approve or reject decision using Command(resume=...)

For destructive or expensive operations you often want a human to approve
before the agent acts. interrupt_on pauses the run and surfaces the
pending tool call as an interrupt; you then resume with a decision
("approve" or "reject"). A checkpointer is required so the paused run can
be restored. Here we reject one deletion and approve another to show both
control paths.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/human-in-the-loop
-----------------------------------------------------------------------
"""


# --- 1. Define a sensitive tool ---
def delete_file(name: str) -> str:
    """Permanently delete a file by name."""
    print(f"  [tool] delete_file({name!r}) EXECUTED")
    return f"Deleted {name}"


# --- 2. Create the agent, requiring approval for delete_file ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    tools=[delete_file],
    system_prompt="You are a file assistant. Use delete_file when asked. Reply in one sentence.",
    interrupt_on={"delete_file": True},  # pause before delete_file runs
    checkpointer=InMemorySaver(),  # required to pause and resume
)


def run_with_decision(thread_id: str, request: str, decision: str) -> None:
    """Start a run, hit the approval interrupt, then resume with a decision."""
    config = {"configurable": {"thread_id": thread_id}}

    # First invoke pauses at the interrupt
    result = agent.invoke({"messages": [{"role": "user", "content": request}]}, config=config)
    interrupt = result["__interrupt__"][0]
    pending = interrupt.value["action_requests"][0]
    print(f"  PAUSED — agent wants to call {pending['name']}({pending['args']})")
    print(f"  Human decision: {decision.upper()}")

    # Resume with the human's decision
    resumed = agent.invoke(
        Command(resume={"decisions": [{"type": decision}]}),
        config=config,
    )
    print(f"  Agent: {resumed['messages'][-1].text}")


# --- 3. Reject a deletion ---
print("=== Deep Agents Human-in-the-Loop ===")
print("\n[Case 1] Reject the deletion:")
run_with_decision("thread-reject", "Delete the file important.txt", "reject")

# --- 4. Approve a deletion ---
print("\n[Case 2] Approve the deletion:")
run_with_decision("thread-approve", "Delete the file temp.log", "approve")
