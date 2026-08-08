import os
import json
import asyncio
import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import to_mcp_server
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import TextContent

from settings import settings

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

# Suppress the SDK's "non-text parts in response" informational warning
logging.getLogger("google_genai.types").setLevel(logging.ERROR)

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- to_mcp_server: publishing a whole ADK agent as an MCP server
- Single-tool exposure: the agent's own tools stay private to the agent
- Progress notifications: intermediate agent text streamed to the MCP host
- Per-connection sessions: successive tool calls form one conversation

This is the exact inverse of 11_mcp_tools.py. There an ADK agent *consumed*
an external MCP server; here the ADK agent *is* the MCP server, so any MCP
host (an IDE, a coding agent, another framework) can delegate work to it
without importing ADK. We drive it with an in-memory MCP client so the
example stays self-contained instead of blocking on a stdio transport.

For more details, visit:
https://github.com/google/adk-python/blob/v2.6.2/docs/guides/tools/mcp_tool/agent_to_mcp/index.md
-------------------------------------------------------
"""


# --- 1. Build a normal ADK agent with its own private tools ---


def get_order_status(order_id: str) -> dict[str, Any]:
    """Looks up the delivery status of a customer order."""
    orders = {
        "ORD-42": {"status": "shipped", "carrier": "DHL", "eta_days": 2},
        "ORD-77": {"status": "processing", "carrier": None, "eta_days": 5},
    }
    return orders.get(order_id, {"status": "unknown"})


def get_return_window(order_id: str) -> dict[str, Any]:
    """Returns how many days are left to return an order."""
    return {"order_id": order_id, "days_left": 14}


support_agent = LlmAgent(
    name="support_agent",
    model=settings.GOOGLE_MODEL_NAME,
    description="Answers customer questions about order status and returns.",
    instruction=(
        "You are a customer support agent. Use get_order_status and "
        "get_return_window to answer. Before each tool call, state in one short "
        "sentence what you are about to check. Answer in one sentence."
    ),
    tools=[get_order_status, get_return_window],
)


# --- 2. Publish the agent as an MCP server ---
#
# The whole agent becomes ONE MCP tool named after it. A host sends a `request`
# string and gets the agent's final response; it never sees get_order_status or
# get_return_window. The caller picks the transport — a real deployment would
# call server.run(transport="stdio") here, which blocks forever, so this example
# connects an in-memory client instead.

server = to_mcp_server(support_agent)


async def main() -> None:
    async with create_connected_server_and_client_session(server) as client:
        # --- 3. Discover what the host sees ---

        print("-" * 65)
        print("  What an MCP host discovers on this server")
        print("-" * 65)

        tools = (await client.list_tools()).tools
        print(f"  Tools exposed: {len(tools)}  (the agent's 2 tools stay private)")
        for tool in tools:
            print(f"    name:        {tool.name}")
            print(f"    description: {tool.description}")
            print(f"    inputSchema: {json.dumps(tool.inputSchema)}")

        tool_name = tools[0].name

        # --- 4. Call the agent through MCP, collecting progress notifications ---
        #
        # to_mcp_server forwards the agent's intermediate text as MCP progress
        # notifications, so the host can show the agent working.

        progress_messages: list[str] = []

        async def on_progress(progress: float, total: float | None, message: str | None):
            if message:
                progress_messages.append(message)
                print(f"    [progress] {message.strip()}")

        print("\n" + "-" * 65)
        print("  Call 1: 'Where is order ORD-42?'")
        print("-" * 65)
        result = await client.call_tool(
            tool_name, {"request": "Where is order ORD-42?"}, progress_callback=on_progress
        )
        for block in result.content:
            if isinstance(block, TextContent):
                print(f"  Agent: {block.text.strip()}")

        # --- 5. A second call on the same connection continues the conversation ---
        #
        # One ADK session is kept per MCP connection, so the agent still knows
        # which order we are talking about.

        print("\n" + "-" * 65)
        print("  Call 2: 'How long do I have to return it?' (same connection)")
        print("-" * 65)
        result = await client.call_tool(
            tool_name,
            {"request": "How long do I have to return it?"},
            progress_callback=on_progress,
        )
        for block in result.content:
            if isinstance(block, TextContent):
                print(f"  Agent: {block.text.strip()}")

        print("\n" + "-" * 65)
        print("  Summary")
        print("-" * 65)
        print(f"  MCP tools exposed:            1 ({tool_name})")
        print("  Agent tools visible to host:  0 (encapsulated behind the agent)")
        print(f"  Progress notifications sent:  {len(progress_messages)}")
        print("  Call 2 resolved 'it' from call 1 — same ADK session per connection.")


if __name__ == "__main__":
    asyncio.run(main())
