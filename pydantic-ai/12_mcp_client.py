import asyncio

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.toolsets import PrefixedToolset

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Connecting to MCP (Model Context Protocol) servers with MCPToolset
- Running an in-process FastMCP server so the example needs no subprocess
- Using MCP tools as agent toolsets
- PrefixedToolset to namespace MCP tool names and avoid collisions

MCP is an open protocol that lets AI agents discover and use tools
exposed by external servers. MCPToolset is built on the FastMCP client,
so it accepts anything FastMCP can build a transport from: an HTTP/SSE
URL, a stdio script path, a pre-built client, or -- as used here -- an
in-process FastMCP server instance.

NOTE: v2 replaced MCPServerStdio/MCPServerSSE/MCPServerStreamableHTTP with
the single MCPToolset, which takes one positional argument instead of a
command plus args. Its `tool_prefix` argument was removed repo-wide; wrap
the toolset in PrefixedToolset instead.

For more details, visit:
https://pydantic.dev/docs/ai/mcp/client/
-----------------------------------------------------------------------
"""


# --- 1. Define a small in-process MCP server ---
# Any MCP server works here (a URL or a stdio script path); an in-process
# server keeps the example self-contained and free of external processes.
mcp_server = FastMCP("file-tools", log_level="WARNING")


@mcp_server.tool()
def list_files(directory: str) -> str:
    """List the files in a directory."""
    listings = {
        ".": "settings.py, utils.py, 12_mcp_client.py",
        "res": "agent_graph.png",
    }
    return listings.get(directory, f"No such directory: {directory}")


@mcp_server.tool()
def read_file(path: str) -> str:
    """Read the contents of a file."""
    files = {
        "settings.py": 'OPENAI_MODEL_NAME: str = "openai-chat:gpt-4o-mini"',
        "utils.py": "def show_metrics(usage): ...",
    }
    return files.get(path, f"No such file: {path}")


# --- 2. Helper that reveals which tool names the model actually called ---
def tool_calls(result) -> list[str]:
    """Collect the called tool names, which proves the fs_ prefix is applied."""
    return [
        part.tool_name
        for message in result.all_messages()
        for part in getattr(message, "parts", [])
        if hasattr(part, "tool_name") and hasattr(part, "args")
    ]


async def main():
    print("=== MCP Client Example ===\n")

    # --- 3. Wrap the MCP server in a toolset, then namespace its tools ---
    # tool_prefix= was removed in v2; PrefixedToolset does the same job for
    # any toolset, so `list_files` is offered to the model as `fs_list_files`.
    mcp_toolset = PrefixedToolset(MCPToolset(mcp_server), "fs")

    # --- 4. Create agent with the MCP toolset ---
    agent = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions=(
            "You are a file system assistant. Every file operation must go "
            "through the tools: list a directory with the listing tool, and "
            "read a file's contents with the reading tool. Be concise."
        ),
        toolsets=[mcp_toolset],
    )

    # --- 5. Run the agent with MCP tools ---
    async with agent:
        print("Step 1: Listing files through the MCP server...")
        result = await agent.run("List the files in the current directory.")
        print(f"Response: {result.output}")
        print(f"MCP tools called: {tool_calls(result)}")
        print()

        print("Step 2: Reading a file through the MCP server...")
        result2 = await agent.run(
            "Read the settings.py file and tell me what model is configured."
        )
        print(f"Response: {result2.output}")
        print(f"MCP tools called: {tool_calls(result2)}")


if __name__ == "__main__":
    asyncio.run(main())
