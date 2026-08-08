import asyncio
import sys
from typing import Any

from dotenv import load_dotenv

from agent_framework import Agent, AgentResponse, MCPStdioTool
from agent_framework.openai import OpenAIChatClient

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Microsoft Agent Framework
with the following features:
- MCPStdioTool(use_progressive_disclosure=True) for on-demand schemas
- always_load=[...] to keep a few cheap tools permanently visible
- allowed_tools=[...] as a hard boundary the model cannot cross
- Generated <prefix>_list_mcp_tools / _load_tool / _unload_tool

Example 09 loads every tool a server offers into the prompt up
front, which does not scale to large MCP servers. With progressive
disclosure the model instead lists what exists, loads only the
schema it needs for the next iteration, and unloads it afterwards.
allowed_tools is a separate, stricter thing: tools left out of it
are never listed and can never be loaded, no matter what the model asks.

For more details, visit:
https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools?pivots=programming-language-python
-------------------------------------------------------
"""

ALWAYS_VISIBLE = "get_server_status"
LOADABLE = "search_docs"
FORBIDDEN = "internal_admin_report"


# --- 1. A tiny local MCP server, run as a child process ---
async def run_demo_server() -> None:
    """Serves three tools over stdio: one visible, one loadable, one filtered out."""
    import mcp.types as types
    from mcp.server.lowlevel import Server
    from mcp.server.stdio import stdio_server

    server: Server[Any, Any] = Server("progressive-disclosure-demo")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name=ALWAYS_VISIBLE,
                description="Return the health of the demo MCP server.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name=LOADABLE,
                description="Search documentation snippets about MCP progressive disclosure.",
                inputSchema={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            ),
            types.Tool(
                name=FORBIDDEN,
                description="Internal server details, intentionally excluded by allowed_tools.",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> types.CallToolResult:
        if name == ALWAYS_VISIBLE:
            text = "The demo MCP server is healthy. Use search_docs for the details."
        elif name == LOADABLE:
            query = str(arguments.get("query", "")) or "progressive disclosure"
            text = (
                f"Results for '{query}': the agent starts with list/load/unload tools plus "
                "the always-loaded ones. load_tool adds an allowed remote tool to the live "
                "tool list for the next model iteration; unload_tool removes it again."
            )
        else:
            text = "This tool should never have been reachable."
        return types.CallToolResult(content=[types.TextContent(type="text", text=text)])

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def print_tool_calls(result: AgentResponse) -> None:
    """Prints the tool calls the model made, in order."""
    calls = [
        content.name
        for message in result.messages
        for content in message.contents
        if content.type == "function_call"
    ]
    print("Tools called, in order:")
    for name in calls:
        print(f"  - {name}")
    print(f"Forbidden tool reached: {any(FORBIDDEN in str(name) for name in calls)}")


async def run_agent() -> None:
    # --- 2. Configure the MCP tool for progressive disclosure ---
    mcp_tool = MCPStdioTool(
        name="DocsMCP",
        description="Demo MCP server with progressively loaded documentation tools.",
        command=sys.executable,
        args=[__file__, "--server"],
        # Hard boundary: internal_admin_report is absent, so it can never be
        # listed or loaded — unlike the merely-hidden search_docs.
        allowed_tools=[ALWAYS_VISIBLE, LOADABLE],
        use_progressive_disclosure=True,
        always_load=[ALWAYS_VISIBLE],
        tool_name_prefix="docs",
        load_prompts=False,
    )

    client = OpenAIChatClient(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    # --- 3. Run the agent; it discovers, loads, uses and unloads a tool ---
    async with Agent(
        client=client,
        name="docs-agent",
        instructions=(
            "Call docs_list_mcp_tools to see which MCP tools exist. If you need a "
            "hidden one, call docs_load_tool with its remote name, then call the "
            "newly available prefixed tool on the next iteration, and finally "
            "docs_unload_tool. Never invent tools that were not listed. Be concise."
        ),
        tools=mcp_tool,
    ) as agent:
        prompt = (
            "Explain how progressive MCP tool disclosure works. Inspect the MCP tools "
            f"you can load, load {LOADABLE}, use it, then unload it. Also try to call "
            f"{FORBIDDEN} and report what happened."
        )
        print("=== MCP Progressive Disclosure ===")
        print(f"User: {prompt}\n")
        result = await agent.run(prompt)

        # --- 4. Show the discovery path and the enforced boundary ---
        print_tool_calls(result)
        print(f"\nAgent: {result.text}")


async def main() -> None:
    if "--server" in sys.argv:
        await run_demo_server()
    else:
        await run_agent()


if __name__ == "__main__":
    asyncio.run(main())
