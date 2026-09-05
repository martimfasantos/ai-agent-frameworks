from dotenv import load_dotenv

from agno.agent import Agent
from agno.approval.decorator import approval
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.utils.pprint import pprint_run_response

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Agno with the following features:
- The @approval decorator for tool-level HITL gating
- ApprovalType.required for blocking approval before execution
- Composing @approval with @tool in either order

The @approval decorator (new in Agno 2.6.x) provides a cleaner
way to mark tools as requiring human approval. It replaces the
older requires_confirmation=True pattern on @tool with a
composable decorator that supports both required (blocking)
and audit (non-blocking) approval types.

For more details, visit:
https://docs.agno.com/runtime/human-approval
-------------------------------------------------------
"""


# --- 1. Define tools with @approval decorator ---
@approval
@tool
def delete_file(filename: str) -> str:
    """Delete a file from the system.

    Args:
        filename: The name of the file to delete.

    Returns:
        Confirmation that the file was deleted.
    """
    return f"File '{filename}' has been deleted."


@tool
def list_files() -> str:
    """List all files in the current directory.

    Returns:
        A list of files.
    """
    return "Files: report.pdf, notes.txt, budget.xlsx, photo.jpg"


# --- 2. Create the agent ---
agent = Agent(
    model=OpenAIChat(id=settings.OPENAI_MODEL_NAME),
    tools=[delete_file, list_files],
    instructions=[
        "You are a file management assistant.",
        "When asked to delete files, use the delete_file tool.",
        "When asked to list files, use the list_files tool.",
        "Be concise in your responses.",
    ],
    markdown=True,
)

# --- 3. Run a safe operation (no approval needed) ---
print("=== Example 1: Safe operation (list files) ===\n")
run_output = agent.run("List all the files.")
pprint_run_response(run_output)

# --- 4. Run a destructive operation (approval required) ---
print("\n=== Example 2: Destructive operation (delete file — needs approval) ===\n")
run_output = agent.run("Delete the file notes.txt")
pprint_run_response(run_output)

# Check for pending requirements
if run_output.requirements:
    print(f"\nPending approvals: {len(run_output.requirements)}")
    for req in run_output.requirements:
        tool_exec = req.tool_execution
        if tool_exec:
            print(f"  Tool: {tool_exec.tool_name}")
            print(f"  Args: {tool_exec.tool_args}")

    # Approve and continue
    for req in run_output.requirements:
        req.confirm()

    print("\n=== Continuing after approval ===\n")
    continued_output = agent.continue_run(
        run_response=run_output,
        requirements=run_output.requirements,
    )
    pprint_run_response(continued_output)
else:
    print("\nNo approval needed — tool executed directly.")
