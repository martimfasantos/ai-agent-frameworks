import asyncio
import os
import sys

from ag2 import Agent
from ag2.config import OpenAIConfig
from ag2.events import ToolCallEvent, ToolResultEvent
from ag2.tools import MCPStdioServerConfig, MCPToolkit

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- MCPToolkit: client-side connection to an MCP server
- MCPStdioServerConfig to launch a local server as a subprocess
- MCP tools appearing to the model as ordinary function tools

AG2 1.0 replaces create_toolkit() with MCPToolkit, a Toolkit you
pass straight into tools=. It discovers the server's tools lazily
and executes them locally, so the pattern works with any provider.
This example drives the local calculator server in mcp_server.py.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/tools/mcp_servers.mdx
-------------------------------------------------------
"""


async def main() -> None:
    # --- 1. Point the toolkit at the local stdio MCP server ---
    toolkit = MCPToolkit(
        MCPStdioServerConfig(
            command=sys.executable,
            args=["mcp_server.py"],
            server_label="calculator",
        )
    )

    # --- 2. Create the agent with the MCP toolkit as its tools ---
    agent = Agent(
        "calculator",
        prompt=(
            "You are a calculator agent. Use the provided tools for every "
            "arithmetic step — never compute in your head. State the final "
            "answer in one sentence."
        ),
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        tools=[toolkit],
    )

    # --- 3. Run a calculation that needs two of the server's tools ---
    # The subprocess is launched lazily, on the first tool discovery.
    print("=== Calculation ===\n")
    reply = await agent.ask("Calculate (15 + 27) * 3 using the tools.")
    print(f"Agent: {reply.body}")

    # --- 4. Prove the MCP tools actually executed ---
    print("\n=== MCP tool activity ===")
    for event in await reply.context.stream.history.get_events():
        if isinstance(event, ToolCallEvent):
            print(f"  -> {event.name}({event.arguments})")
        elif isinstance(event, ToolResultEvent):
            text = " ".join(str(part.content) for part in event.result.parts)
            print(f"  <- {text}")


if __name__ == "__main__":
    asyncio.run(main())
