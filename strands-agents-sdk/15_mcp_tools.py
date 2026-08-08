from strands import Agent
from strands.tools.mcp import MCPClient

"""
-------------------------------------------------------
In this example, we explore Strands Agents SDK with the following features:
- MCP (Model Context Protocol) tool integration
- MCPClient with stdio transport
- Streamable HTTP and SSE transports
- Context manager and managed lifecycle patterns
- continue_on_error, progress_callback and application_name (new in v1.45.0/v1.47.0)

MCP lets you connect to external tool servers using a standard protocol.
Strands supports stdio, streamable HTTP, and SSE transports. You can pass
an MCPClient directly to the Agent for managed lifecycle, or use a context
manager for explicit control.

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/
-------------------------------------------------------
"""

# --- 1. Overview ---
print("=== MCP Tools Integration ===\n")
print("MCP (Model Context Protocol) enables agents to discover and use")
print("tools from external servers via a standardized protocol.\n")

# --- 2. Stdio transport pattern ---
print("--- Example 1: Stdio Transport ---\n")

stdio_code = """
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

# Configure stdio transport to a local MCP server
mcp_client = MCPClient(
    lambda: stdio_client(StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    ))
)

# Option A: Context manager (explicit lifecycle control)
with mcp_client:
    agent = Agent(tools=[mcp_client])
    result = agent("List the files in the /tmp directory.")
    print(result.message)

# Option B: Managed lifecycle (agent manages the MCP client)
agent = Agent(tools=[mcp_client])
result = agent("List the files in the /tmp directory.")
print(result.message)
"""
print(stdio_code)

# --- 3. Streamable HTTP transport ---
print("--- Example 2: Streamable HTTP Transport ---\n")

http_code = """
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient

mcp_client = MCPClient(
    lambda: streamablehttp_client("http://localhost:8080/mcp")
)

with mcp_client:
    agent = Agent(tools=[mcp_client])
    result = agent("Query the database for recent records.")
    print(result.message)
"""
print(http_code)

# --- 4. SSE transport ---
print("--- Example 3: SSE Transport ---\n")

sse_code = """
from mcp.client.sse import sse_client
from strands import Agent
from strands.tools.mcp import MCPClient

mcp_client = MCPClient(
    lambda: sse_client("http://localhost:8080/sse")
)

with mcp_client:
    agent = Agent(tools=[mcp_client])
    result = agent("What tools are available?")
    print(result.message)
"""
print(sse_code)

# --- 5. Creating an MCP server ---
print("--- Example 4: Creating an MCP Server ---\n")

server_code = '''
from mcp.server import FastMCP

mcp = FastMCP("Demo MCP Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b

# Run: python server.py
mcp.run()
'''
print(server_code)

# --- 6. Client resilience and observability options ---
print("--- Example 5: Client Options ---\n")

options_code = '''
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient

async def on_progress(progress: float, total: float | None, message: str | None) -> None:
    """Called for every progress notification the server emits."""
    print(f"{progress}/{total} {message or ''}")

mcp_client = MCPClient(
    lambda: streamablehttp_client("http://localhost:8080/mcp"),
    # Identify this client to the server (shows up in its logs)
    application_name="strands-examples",
    # Keep the agent alive when one server in a multi-server setup fails
    continue_on_error=True,
    # Receive progress notifications from long-running tools
    progress_callback=on_progress,
)

with mcp_client:
    agent = Agent(tools=[mcp_client])
    result = agent("Run the long import job.")
'''
print(options_code)

# --- 7. Summary ---
print("--- Summary ---")
print("MCP transports supported by Strands:")
print("  - stdio: Local process communication (npx, python, etc.)")
print("  - streamable HTTP: Remote HTTP-based MCP servers")
print("  - SSE: Server-Sent Events transport")
print("\nUsage: Pass MCPClient to Agent(tools=[mcp_client])")
print("The agent auto-discovers all tools from the MCP server.")
print("\nClient options: application_name, continue_on_error, progress_callback,")
print("elicitation_callback, tool_filters, prefix, startup_timeout.")
