import os
import asyncio
import logging
import tempfile

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters

from settings import settings

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

# Suppress the SDK's "non-text parts in response" informational warning
logging.getLogger("google_genai.types").setLevel(logging.ERROR)

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- MCP Tools: connecting an ADK agent to an external MCP server
- McpToolset: the ADK class that wraps an MCP server as a toolset
- StdioConnectionParams: launching a local MCP server via stdin/stdout
- Tool discovery: the agent automatically uses tools exposed by the MCP server
- Lifecycle management: properly closing the MCP connection after use

The Model Context Protocol (MCP) standardizes how LLMs communicate with
external tools and data sources. This example uses the community
@modelcontextprotocol/server-filesystem MCP server (via npx), which exposes
tools for reading directories and files. The ADK agent discovers these tools
automatically and uses them to answer questions about a temporary directory.

For more details, visit:
https://google.github.io/adk-docs/tools-custom/mcp-tools/
-------------------------------------------------------
"""

APP_NAME = "mcp_demo"
USER_ID = "user"
SESSION_ID = "session_1"


async def run_demo() -> None:
    # --- 1. Create a temporary directory with sample files for the demo ---

    with tempfile.TemporaryDirectory() as tmp_dir:
        # On macOS /tmp is a symlink to /private/tmp; resolve to the canonical path
        # so the MCP server's allowed directory matches paths returned by list_directory
        tmp_dir = os.path.realpath(tmp_dir)
        with open(os.path.join(tmp_dir, "notes.txt"), "w") as f:
            f.write("Meeting at 3pm on Friday.\nBuy groceries.\nCall the dentist.\n")
        with open(os.path.join(tmp_dir, "readme.md"), "w") as f:
            f.write("# Project Notes\nThis folder contains personal notes and tasks.\n")
        with open(os.path.join(tmp_dir, "tasks.txt"), "w") as f:
            f.write("1. Finish the report\n2. Review pull requests\n3. Update docs\n")

        print(f"\nDemo folder: {tmp_dir}")
        print(f"Files: {os.listdir(tmp_dir)}\n")

        # --- 2. Create McpToolset pointing at the local filesystem MCP server ---

        toolset = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        tmp_dir,  # absolute path to the folder the server can access
                    ],
                ),
                timeout=30,  # seconds to wait for the MCP server to start
            ),
            tool_filter=["list_directory", "read_file"],  # expose only these two tools
        )

        # --- 3. Create the agent with the MCP toolset ---

        agent = LlmAgent(
            name="FilesystemAssistant",
            model=settings.GOOGLE_MODEL_NAME,
            instruction=(
                f"You are a helpful file assistant. "
                f"The working directory is: {tmp_dir}. "
                f"When listing a directory, use the full path: {tmp_dir}. "
                f"When reading files, use full paths like {tmp_dir}/notes.txt. "
                "Be concise — answer in 1-3 sentences or a short bullet list."
            ),
            tools=[toolset],
        )

        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

        async def send(query: str) -> str:
            message = types.Content(role="user", parts=[types.Part(text=query)])
            response_text = ""
            async for event in runner.run_async(
                user_id=USER_ID, session_id=SESSION_ID, new_message=message
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    response_text = event.content.parts[0].text or ""
            return response_text

        # --- 4. Demonstrate tool discovery and usage ---

        print("-" * 65)
        print("  Query 1: List files in the demo directory")
        print("-" * 65)
        reply = await send(f"List all files in {tmp_dir}")
        print(f"  Agent: {reply.strip()}")

        print("\n" + "-" * 65)
        print("  Query 2: Read a specific file via MCP tool")
        print("-" * 65)
        reply = await send(f"Read the contents of {tmp_dir}/notes.txt")
        print(f"  Agent: {reply.strip()}")

        print("\n" + "-" * 65)
        print("  Query 3: Read another file")
        print("-" * 65)
        reply = await send(f"What tasks are listed in {tmp_dir}/tasks.txt?")
        print(f"  Agent: {reply.strip()}")
        print()

        # --- 5. Clean up the MCP server connection ---
        await toolset.close()


if __name__ == "__main__":
    asyncio.run(run_demo())
