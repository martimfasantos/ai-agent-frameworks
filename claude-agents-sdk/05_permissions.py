import asyncio
import warnings
from collections.abc import AsyncIterable
from typing import Any

from dotenv import load_dotenv

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    AssistantMessage,
    ToolUseBlock,
    CanUseTool,
    ToolPermissionContext,
    PermissionResult,
    PermissionResultAllow,
    PermissionResultDeny,
    CanUseToolShadowedWarning,
)

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Claude Agent SDK with the following features:
- Permission modes: default, acceptEdits, plan, bypassPermissions
- allowed_tools and disallowed_tools for fine-grained control
- can_use_tool callback for programmatic permission decisions
- CanUseToolShadowedWarning when allowed_tools silently bypasses the callback

Permission modes control how broadly tools are auto-approved. The
allowed_tools list acts as a per-tool allowlist, while disallowed_tools
blocks specific tools. For dynamic control, the can_use_tool callback
lets you inspect each tool call and decide at runtime.

For more details, visit:
https://platform.claude.com/docs/en/agent-sdk/permissions
-------------------------------------------------------
"""

# --------------------------------------------------------------
# Example 1: Permission Mode + Allowed/Disallowed Tools
# --------------------------------------------------------------
print("=== Example 1: Permission Mode with Allow/Deny Lists ===")


async def example_permission_lists():
    options = ClaudeAgentOptions(
        # Allow Read and Glob but deny Bash for safety
        allowed_tools=["Read", "Glob"],
        disallowed_tools=["Bash"],
        permission_mode="default",
    )

    async for message in query(
        prompt="List all .py files in the current directory using Glob.",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"[Tool Call] {block.name}")
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"\nResult: {message.result}")


asyncio.run(example_permission_lists())

# --------------------------------------------------------------
# Example 2: can_use_tool Callback
# --------------------------------------------------------------
print("\n=== Example 2: can_use_tool Callback ===")

# Track tool usage for audit logging
tool_audit_log: list[str] = []


async def permission_callback(
    tool_name: str,
    tool_input: dict[str, Any],
    context: ToolPermissionContext,
) -> PermissionResult:
    """Custom permission callback that logs and filters tool calls."""
    tool_audit_log.append(f"{tool_name}({tool_input})")
    print(f"  [Permission Check] {tool_name} requested")

    # Allow read-only tools, deny anything that writes
    read_only_tools = {"Read", "Glob", "Grep"}
    if tool_name in read_only_tools:
        return PermissionResultAllow(behavior="allow")

    return PermissionResultDeny(
        behavior="deny",
        message=f"Tool '{tool_name}' is not allowed by policy.",
    )


async def streaming_prompt(text: str) -> AsyncIterable[dict[str, Any]]:
    """Wrap a string prompt as an AsyncIterable for streaming mode."""
    yield {
        "type": "user",
        "message": {"role": "user", "content": text},
        "parent_tool_use_id": None,
        "session_id": None,
    }


async def example_can_use_tool():
    options = ClaudeAgentOptions(
        can_use_tool=permission_callback,
    )

    # can_use_tool requires streaming mode, so we pass an AsyncIterable prompt
    async for message in query(
        prompt=streaming_prompt(
            "Read the contents of settings.py in the current directory."
        ),
        options=options,
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"\nResult: {message.result}")

    print(f"\nAudit log ({len(tool_audit_log)} calls): {tool_audit_log}")


asyncio.run(example_can_use_tool())

# --------------------------------------------------------------
# Example 3: can_use_tool Shadowed by allowed_tools
# --------------------------------------------------------------
print("\n=== Example 3: can_use_tool Shadowed by allowed_tools ===")


async def example_shadowed_callback():
    # A whole-tool allowed_tools entry auto-approves before the callback runs,
    # so the callback never sees the call. Since 0.2.111 the SDK warns about it.
    options = ClaudeAgentOptions(
        can_use_tool=permission_callback,
        allowed_tools=["Read"],
    )

    calls_before = len(tool_audit_log)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")

        async for message in query(
            prompt=streaming_prompt("Read settings.py and say how many lines it has."),
            options=options,
        ):
            if isinstance(message, ResultMessage) and message.subtype == "success":
                print(f"Result: {message.result}")

    for warning in caught:
        if issubclass(warning.category, CanUseToolShadowedWarning):
            print(f"\n[{warning.category.__name__}] {warning.message}")

    print(f"\nCallback invocations during this run: {len(tool_audit_log) - calls_before}")
    print("Use a PreToolUse hook to gate tools that allowed_tools already approves.")


asyncio.run(example_shadowed_callback())
