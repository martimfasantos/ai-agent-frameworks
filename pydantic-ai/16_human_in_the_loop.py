import asyncio
import json

from dotenv import load_dotenv
from pydantic_ai import (
    Agent,
    ApprovalRequired,
    DeferredToolRequests,
    DeferredToolResults,
    RunContext,
    ToolApproved,
    ToolDenied,
)

from utils import show_metrics
from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Human-in-the-loop tool approval
- Two approval patterns: requires_approval=True and ApprovalRequired exception
- DeferredToolRequests output pausing agent execution for approval
- DeferredToolResults providing approval or denial decisions
- Continuing agent execution with message history after approval

Human-in-the-loop approval enables safe execution of sensitive operations by requiring
explicit human authorization. Tools can conditionally or always require approval,
and the agent pauses execution until receiving approval decisions for each tool call.

For more details, visit:
https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#human-in-the-loop-tool-approval
-----------------------------------------------------------------------
"""

# --- 1. Create agent that can return deferred tool requests ---
agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=[str, DeferredToolRequests],  # Must include DeferredToolRequests
    system_prompt="You help manage files. Use tools to complete user requests.",
)

# Protected files requiring approval
PROTECTED_FILES = {".env", "config.yml", "secrets.json"}

# --- 2. Define tools with different approval patterns ---


# Pattern 1: Conditional approval based on arguments/context
@agent.tool
def read_file(ctx: RunContext, filename: str) -> str:
    """Read a file."""
    # Check if this specific call needs approval
    if filename in PROTECTED_FILES and not ctx.tool_call_approved:
        # Raise exception to defer this call for approval
        raise ApprovalRequired(f"File {filename} is protected")

    # If approved or not protected, execute
    return f"Updated {filename} with: [file content here]"


# Pattern 2: Always requires approval
@agent.tool_plain(requires_approval=True)
def delete_file(filename: str) -> str:
    """Delete a file."""
    return f"Deleted {filename}"


# --- 3. Run the workflow with approval ---
async def main():
    print("=== Human-in-the-Loop Tool Approval ===\n")

    print("Step 1: Initial agent run")
    print("=" * 60)

    # Run agent with multiple tasks
    result = await agent.run(
        "Read the README.md file, read the .env and delete temp.log"
    )
    messages = result.all_messages()

    # --- 4. Check if approval is needed ---
    requests = result.output
    print(f"Agent needs approval for {len(requests.approvals)} tool calls:\n")

    # Display all pending approvals
    for i, call in enumerate(requests.approvals, 1):
        if isinstance(call.args, dict):
            args_str = ", ".join(f"{k}={v!r}" for k, v in call.args.items())
        else:
            args_str = str(call.args)
        print(f"  {i}. {call.tool_name}({args_str})")
    print()

    # --- 5. Simulate human decision-making ---
    print("Step 2: Human decision-making")
    print("=" * 60)

    results = DeferredToolResults()

    for call in requests.approvals:
        # convert str to dict if necessary
        if isinstance(call.args, str):
            args = json.loads(call.args)
        else:
            args = call.args

        if call.tool_name == "read_file":
            if args.get("filename") in PROTECTED_FILES:
                # Deny reading sensitive files
                print(f"  Denied: read_file('{args.get('filename')}')")
                print(f"   Reason: Cannot read sensitive configuration")

            # Approve all Reads for next run
            results.approvals[call.tool_call_id] = ToolApproved()
            # OR results.approvals[call.tool_call_id] = True

        elif call.tool_name == "delete_file":
            print(f"  Deleting files is not allowed")

            # Keep denying deletions
            results.approvals[call.tool_call_id] = ToolDenied(
                "File deletion not allowed"
            )

    print()

    # --- 6. Continue agent run with approval results ---
    print("Step 3: Continue execution with approved Reads but denied Deletes")
    print("=" * 60)

    final_result = await agent.run(
        message_history=messages,  # Continue from where we left off
        deferred_tool_results=results,  # Provide changed approval decisions
    )

    print(f"\nFinal result:\n{final_result.output}\n")


if __name__ == "__main__":
    asyncio.run(main())
