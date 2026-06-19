import asyncio

from dotenv import load_dotenv

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    AssistantMessage,
    ToolUseBlock,
)

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Claude Agent SDK with the following features:
- strict_mcp_config to lock down MCP server sources
- Preventing project/user/global MCP configs from loading
- Ensuring deterministic, reproducible tool sets

When strict_mcp_config=True, the SDK ignores all MCP servers defined
in project-level (.mcp.json), user-level, and global configurations.
Only the servers you pass explicitly via mcp_servers are available.
This is essential for CI/CD pipelines, security-sensitive environments,
and any deployment where you need a fully deterministic tool set.

For more details, visit:
https://platform.claude.com/docs/en/agent-sdk/mcp
-------------------------------------------------------
"""

# --- 1. Configure with strict MCP config ---
print("=== Strict MCP Config Demo ===\n")

# With strict_mcp_config=True, only explicitly-passed MCP servers are used.
# No project, user, or global MCP configs are loaded.
options = ClaudeAgentOptions(
    strict_mcp_config=True,
    # No mcp_servers passed — agent has zero external MCP tools
    allowed_tools=["Read", "Glob"],
    permission_mode="bypassPermissions",
)


# --- 2. Run a query — only built-in tools are available ---
async def main():
    print("Running with strict_mcp_config=True (no external MCP servers)...\n")

    async for message in query(
        prompt="List the .py files in the current directory. Use only your built-in tools.",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"[Tool] {block.name}")

        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"\n--- Result ---\n{message.result}")
            print(
                f"\nNote: strict_mcp_config=True ensured no project/user/global MCP servers loaded."
            )


if __name__ == "__main__":
    asyncio.run(main())
