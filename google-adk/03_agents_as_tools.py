import os
import asyncio

from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool, google_search
from google.adk.code_executors import BuiltInCodeExecutor

from settings import settings
from utils import call_agent_async

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- Wrapping agents as tools using AgentTool
- Composing specialist agents under an orchestrator agent
- Using built-in google_search and BuiltInCodeExecutor within sub-agents

In ADK, one agent can call another agent as if it were a tool. This is
different from sub-agent delegation — the orchestrator retains control,
calls the specialist, receives its result, and continues. Here an
orchestrator delegates search to a search agent and code execution to a
coding agent.

For more details, visit:
https://google.github.io/adk-docs/tools-custom/function-tools/#agent-tool
-------------------------------------------------------
"""

# --- 1. Create specialist agents that will be used as tools ---
search_agent = LlmAgent(
    name="search_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction="You are a Google Search specialist. Find accurate, up-to-date information.",
    tools=[google_search],
)

coding_agent = LlmAgent(
    name="coding_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction="You are a Python code execution specialist. Write and run Python code.",
    code_executor=BuiltInCodeExecutor(),
)

# --- 2. Create the orchestrator that uses both agents as tools ---
# Note: as of ADK 2.6.0 direct use of AgentTool is documented as discouraged.
# The recommended alternative is to set mode="single_turn" on the specialist and
# attach it via sub_agents=[...] — ADK then exposes it as a tool automatically
# and runs it inline in the parent's session. AgentTool is kept here because it
# is still the explicit, self-contained way to show the agent-as-tool pattern.
orchestrator = LlmAgent(
    name="orchestrator",
    model=settings.GOOGLE_MODEL_NAME,
    description="Orchestrator agent that delegates to specialist agents.",
    instruction=(
        "You are an orchestrator. Use the available agent tools to answer questions. "
        "Delegate search tasks to the search agent and coding tasks to the coding agent."
    ),
    tools=[
        agent_tool.AgentTool(agent=search_agent),
        agent_tool.AgentTool(agent=coding_agent),
    ],
)

# --- 3. Run the orchestrator ---
query = "Search for a Python script to fetch the current Bitcoin price in USD, then execute it."
print(f"Query: {query}")
asyncio.run(
    call_agent_async(orchestrator, query, tool_calls=True, tool_call_results=True)
)
