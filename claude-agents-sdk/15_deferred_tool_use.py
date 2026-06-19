import asyncio
from typing import Any

from dotenv import load_dotenv

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    HookMatcher,
    HookInput,
    HookJSONOutput,
    HookContext,
    tool,
    create_sdk_mcp_server,
)

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Claude Agent SDK with the following features:
- Deferred tool use for human-in-the-loop (HITL) approval
- PreToolUse hook returning permissionDecision: "defer"
- Inspecting DeferredToolUse on the ResultMessage
- Resuming after reviewing a deferred tool call

When a PreToolUse hook returns "defer", the agent run stops and the
ResultMessage carries a deferred_tool_use field with the tool's ID,
name, and input. Your application can inspect the call, apply policy
checks, or prompt a human for approval before resuming. This is the
recommended pattern for sensitive operations that need oversight.

For more details, visit:
https://platform.claude.com/docs/en/agent-sdk/hooks
-------------------------------------------------------
"""


# --- 1. Define a sensitive tool ---
@tool(
    "delete_record",
    "Delete a database record by ID (destructive operation)",
    {"record_id": str},
)
async def delete_record(args: dict[str, Any]) -> dict[str, Any]:
    """Simulated destructive delete operation."""
    record_id = args["record_id"]
    return {
        "content": [
            {"type": "text", "text": f"Record {record_id} has been deleted."}
        ]
    }


# --- 2. Create MCP server with the tool ---
db_server = create_sdk_mcp_server(
    name="database",
    version="1.0.0",
    tools=[delete_record],
)


# --- 3. Define a hook that defers destructive operations ---
async def defer_destructive_ops(
    hook_input: HookInput,
    tool_use_id: str | None,
    context: HookContext,
) -> HookJSONOutput:
    """Defer any tool call that contains 'delete' for human review."""
    tool_name = hook_input.get("tool_name", "")
    tool_args = hook_input.get("tool_input", {})
    print(f"  [HITL Hook] Tool '{tool_name}' requested with args: {tool_args}")
    print(f"  [HITL Hook] Deferring for human approval...")

    return {
        "continue_": True,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "defer",
            "permissionDecisionReason": "Destructive operation requires human approval.",
        },
    }


# --- 4. Run the agent — it will pause when the tool is deferred ---
print("=== Deferred Tool Use (Human-in-the-Loop) ===")


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"database": db_server},
        allowed_tools=["mcp__database__*"],
        hooks={
            "PreToolUse": [
                HookMatcher(
                    matcher="mcp__database__delete_record",
                    hooks=[defer_destructive_ops],
                ),
            ],
        },
    )

    async for message in query(
        prompt="Delete record with ID 'usr-42' from the database.",
        options=options,
    ):
        if isinstance(message, ResultMessage):
            print(f"\nResult subtype: {message.subtype}")

            if message.deferred_tool_use:
                deferred = message.deferred_tool_use
                print(f"\n--- Deferred Tool Use ---")
                print(f"  Tool ID:    {deferred.id}")
                print(f"  Tool Name:  {deferred.name}")
                print(f"  Tool Input: {deferred.input}")
                print(
                    f"\n  A human reviewer would inspect this and decide to approve or deny."
                )
                print(
                    f"  To resume, pass the session ID back with the approval decision."
                )
            elif message.subtype == "success":
                print(f"Result: {message.result}")


if __name__ == "__main__":
    asyncio.run(main())
