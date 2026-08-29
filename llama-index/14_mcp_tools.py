import asyncio
import logging
import sys

from mcp.server.fastmcp import FastMCP

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import (
    Context,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.llms.openai import OpenAI
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.tools.mcp.utils import workflow_as_mcp

from settings import settings


"""
-------------------------------------------------------
In this example, we explore LlamaIndex with the following features:
- BasicMCPClient to connect to an MCP server over stdio
- McpToolSpec with allowed_tools to expose only chosen MCP tools
- to_tool_list_async() to convert MCP tools into agent tools
- workflow_as_mcp() to publish an existing Workflow as an MCP server
- start_event_model to give the published tool a typed input schema

The Model Context Protocol lets an agent borrow tools from any MCP server, and
lets your own workflows be borrowed by any MCP client. Both directions are
shown here: an agent consumes tools from a server, and a workflow is turned into
one. To keep the example self-contained the MCP server is this same file, which
the client re-launches over stdio with `--serve`.

For more details, visit:
https://developers.llamaindex.ai/python/framework/module_guides/mcp/llamaindex_mcp/
https://developers.llamaindex.ai/python/framework/module_guides/mcp/convert_existing/
-------------------------------------------------------
"""

# FastMCP configures logging at INFO on import, which would drown the demo output
logging.disable(logging.INFO)

# --- 1. A tiny MCP server with mock data ---
mcp_server = FastMCP(name="Weather MCP Server")


@mcp_server.tool()
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    weather = {"lisbon": "sunny, 25C", "oslo": "snowing, -3C"}
    return weather.get(city.lower(), f"No weather data for {city}.")


@mcp_server.tool()
def get_population(city: str) -> str:
    """Get the population of a city."""
    population = {"lisbon": "545,000", "oslo": "709,000"}
    return population.get(city.lower(), f"No population data for {city}.")


# Serving happens before anything else so `--serve` starts a clean stdio server
if __name__ == "__main__" and "--serve" in sys.argv:
    mcp_server.run("stdio")
    sys.exit(0)


# --- 2. A workflow we want other MCP clients to be able to call ---
class QueryEvent(StartEvent):
    """Typed start event — becomes the input schema of the published MCP tool."""
    query: str


class EchoWorkflow(Workflow):
    @step
    async def answer(self, ctx: Context, ev: QueryEvent) -> StopEvent:
        return StopEvent(result=f"EchoWorkflow received: {ev.query}")


async def main():
    llm = OpenAI(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    # --- 3. Connect to the MCP server over stdio ---
    # Passing a command (rather than a URL) makes BasicMCPClient spawn it and
    # speak stdio to the subprocess.
    client = BasicMCPClient(sys.executable, args=[__file__, "--serve"])

    print("Tools advertised by the server:")
    for tool in (await client.list_tools()).tools:
        print(f"  {tool.name}: {tool.description}")

    # --- 4. Convert MCP tools into agent tools, filtered by allowed_tools ---
    tool_spec = McpToolSpec(client=client, allowed_tools=["get_weather"])
    tools = await tool_spec.to_tool_list_async()
    print(f"\nExposed to the agent: {[t.metadata.name for t in tools]}")

    # --- 5. Give them to an agent ---
    agent = FunctionAgent(
        name="mcp_agent",
        description="Answers questions using tools borrowed from an MCP server.",
        system_prompt=(
            "Answer in one short sentence using only the tools available. "
            "If no tool can answer the question, say so instead of guessing."
        ),
        tools=tools,
        llm=llm,
    )
    print(f"\nAgent: {await agent.run('What is the weather in Lisbon?')}")

    # allowed_tools filtered get_population out, so the agent cannot answer this
    print(f"Agent: {await agent.run('What is the population of Lisbon?')}")

    # --- 6. The other direction: publish a workflow as an MCP server ---
    mcp_app = workflow_as_mcp(
        EchoWorkflow(timeout=30),
        workflow_name="echo",
        workflow_description="Echoes a query back to the caller.",
        start_event_model=QueryEvent,
    )
    print("\nWorkflow published as MCP tools:")
    for tool in await mcp_app.list_tools():
        # The start event model becomes the schema of the tool's run_args argument
        schemas = tool.inputSchema.get("$defs", {})
        for name, schema in schemas.items():
            print(f"  {tool.name}(run_args: {name}) fields={sorted(schema['properties'])}")
    # Serve it with: mcp_app.run("streamable-http")


if __name__ == "__main__":
    asyncio.run(main())
