import os
import sys

from mcp import StdioServerParameters

from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI with the following features:
- MCP (Model Context Protocol) server integration
- MCPServerAdapter over a stdio transport, used as a context manager
- Tool discovery from a live MCP server
- Handing the discovered tools to an agent

MCP lets agents connect to external tool servers over a standard protocol.
To keep the example self-contained, the MCP server here is a tiny FastMCP
script started as a subprocess - no external service is required. CrewAI also
accepts a concise DSL string syntax on the agent itself (see the comment
below) as an alternative to the adapter.

For more details, visit:
https://docs.crewai.com/en/mcp/stdio
-------------------------------------------------------
"""

# --- 1. A minimal MCP server, run in-process as a stdio subprocess ---
MCP_SERVER_CODE = '''
from mcp.server.fastmcp import FastMCP

server = FastMCP("warehouse")


@server.tool()
def get_stock(sku: str) -> str:
    """Returns the warehouse stock level for a SKU."""
    return f"{sku}: 42 units in stock"


server.run()
'''

server_params = StdioServerParameters(
    command=sys.executable,
    args=["-c", MCP_SERVER_CODE],
    env=os.environ.copy(),
)

# --- 2. Connect to the server and discover its tools ---
# The adapter starts the server on entry and stops it on exit. Pass tool names
# as extra positional args to expose only a subset.
with MCPServerAdapter(server_params) as mcp_tools:
    print("Discovered MCP tools:", [tool.name for tool in mcp_tools])

    # --- 3. Give the discovered tools to an agent ---
    # The DSL string syntax is an alternative to the adapter and follows the
    # pattern "transport://path_or_url", e.g.:
    #   mcps=["stdio://npx -y @modelcontextprotocol/server-filesystem /tmp"]
    #   mcps=["sse://http://localhost:8000/sse"]
    #   mcps=["streamable-http://http://localhost:8000/mcp"]
    mcp_agent = Agent(
        role="MCP-Enabled Warehouse Assistant",
        goal="Answer stock questions using the MCP tools",
        backstory="You are an assistant with access to an external MCP tool server.",
        tools=mcp_tools,
        llm=settings.OPENAI_MODEL_NAME,
        verbose=True,
    )

    # --- 4. Create and run the crew while the server is still up ---
    task = Task(
        description="How many units of SKU-77 are in stock?",
        expected_output="One sentence with the stock level for SKU-77.",
        agent=mcp_agent,
    )

    crew = Crew(agents=[mcp_agent], tasks=[task], verbose=True)
    result = crew.kickoff()

print("Result:", result.raw)
