import asyncio

from dotenv import load_dotenv

from pydantic_ai import Agent, CodeExecutionTool, WebSearchTool
from pydantic_ai.capabilities import NativeTool

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Native WebSearchTool for grounding responses in live web results
- Native CodeExecutionTool for running Python code in a sandbox
- Wrapping native tools in the NativeTool capability
- Combining multiple native tools in a single agent

Native tools (called "built-in tools" before v2) are pre-configured
capabilities provided by the model provider (e.g. OpenAI). Unlike custom
tools, they run server-side and require no local implementation.
WebSearchTool grounds answers in real search results, while
CodeExecutionTool lets the model write and execute Python code to solve
computational problems.

NOTE: On OpenAI, native tools are only supported on the Responses API,
so this is the one example that overrides the model from settings.py.
In v2 the provider prefix picks the API: `openai-responses:` (also what
a bare `openai:` now means) for the Responses API, `openai-chat:` for
Chat Completions, which does not support these tools.

For more details, visit:
https://pydantic.dev/docs/ai/tools-toolsets/native-tools/
-----------------------------------------------------------------------
"""

# Native tools need the Responses API, so swap the provider prefix while
# keeping the model name configured in settings.py.
RESPONSES_MODEL = "openai-responses:" + settings.OPENAI_MODEL_NAME.split(":")[-1]


# --------------------------------------------------------------
# Example 1: Web Search Tool
# --------------------------------------------------------------
print("=== Example 1: Web Search Tool ===")

# --- 1. Create agent with web search ---
search_agent = Agent(
    model=RESPONSES_MODEL,
    instructions="Answer questions using web search. Be concise (1-2 sentences).",
    capabilities=[
        NativeTool(WebSearchTool(search_context_size="low")),
    ],
)

# --- 2. Run a query that benefits from live data ---
result1 = search_agent.run_sync("What is the current version of Pydantic AI?")
print(f"Response: {result1.output}")
print()


# --------------------------------------------------------------
# Example 2: Code Execution Tool
# --------------------------------------------------------------
print("=== Example 2: Code Execution Tool ===")

# --- 1. Create agent with code execution ---
code_agent = Agent(
    model=RESPONSES_MODEL,
    instructions="Solve problems by writing and executing Python code. Show the result.",
    capabilities=[
        NativeTool(CodeExecutionTool()),
    ],
)

# --- 2. Ask a computational question ---
result2 = code_agent.run_sync(
    "Calculate the first 10 Fibonacci numbers and return them as a list."
)
print(f"Response: {result2.output}")
print()


# --------------------------------------------------------------
# Example 3: Combined Built-in Tools
# --------------------------------------------------------------
print("=== Example 3: Combined Web Search + Code Execution ===")


# --- 1. Create agent with both tools ---
async def run_combined():
    combined_agent = Agent(
        model=RESPONSES_MODEL,
        instructions=(
            "You can search the web for information and execute Python code. "
            "Be concise."
        ),
        capabilities=[
            NativeTool(WebSearchTool(search_context_size="low")),
            NativeTool(CodeExecutionTool()),
        ],
    )

    # Ask something that benefits from code execution
    result3 = await combined_agent.run(
        "What is 2^100? Use code execution to compute the exact value."
    )
    print(f"Response: {result3.output}")


asyncio.run(run_combined())
