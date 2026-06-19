"""
-------------------------------------------------------
In this example, we explore OpenAI Agents SDK with the following features:
- SandboxAgent with a Manifest of workspace files
- Staging files into an isolated sandbox workspace
- Running the agent to analyse staged code

The SandboxAgent provides persistent isolated workspaces for code execution.
A Manifest defines files to stage into the workspace. Since gpt-4o-mini does
not support built-in Capabilities (shell, filesystem), we use a function tool
to simulate file reads. With gpt-5.5+ use Capabilities.default() instead.

For more details, visit:
https://openai.github.io/openai-agents-python/sandbox_agents/
-------------------------------------------------------
"""

import asyncio
import os

from agents import Agent, Runner, function_tool
from agents.extensions.sandbox import Manifest, SandboxAgent

from settings import settings

# ---------------------------------------------------------------------------
# 0. Env setup
# ---------------------------------------------------------------------------
os.environ.setdefault("OPENAI_API_KEY", settings.OPENAI_API_KEY)

# ---------------------------------------------------------------------------
# 1. Workspace files to stage into the sandbox
# ---------------------------------------------------------------------------
HELLO_PY = '''\
def greet(name: str = "World") -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet())
'''

TASK_MD = """\
# Task
Read `hello.py` and answer:
1. What does the code do?
2. List every function name defined in the file.
"""

# ---------------------------------------------------------------------------
# 2. A function tool so gpt-4o-mini can read staged files
# ---------------------------------------------------------------------------
STAGED_FILES: dict[str, str] = {
    "hello.py": HELLO_PY,
    "task.md": TASK_MD,
}


@function_tool
def read_file(filename: str) -> str:
    """Read a file from the sandbox workspace and return its contents."""
    if filename in STAGED_FILES:
        return STAGED_FILES[filename]
    return f"Error: file '{filename}' not found in workspace."


# ---------------------------------------------------------------------------
# 3. Build a SandboxAgent with a Manifest
# ---------------------------------------------------------------------------
def build_sandbox_agent() -> SandboxAgent:
    """Create a SandboxAgent that reviews code in its workspace."""

    manifest = Manifest(
        entries={
            "hello.py": HELLO_PY,
            "task.md": TASK_MD,
        }
    )

    inner_agent = Agent(
        name="Code Reviewer",
        model=settings.OPENAI_MODEL_NAME,
        instructions=(
            "You are a code reviewer. Use the read_file tool to read files "
            "from your workspace. Follow instructions in task.md."
        ),
        tools=[read_file],
    )

    sandbox_agent = SandboxAgent(
        agent=inner_agent,
        manifest=manifest,
    )

    return sandbox_agent


# ---------------------------------------------------------------------------
# 4. Run the sandbox agent
# ---------------------------------------------------------------------------
async def main() -> None:
    print("=== Sandbox Agent Example ===\n")
    print("Running sandbox agent with UnixLocalSandboxClient...\n")

    sandbox_agent = build_sandbox_agent()

    result = await Runner.run(
        sandbox_agent.agent,
        input="Read task.md and follow its instructions. Use the read_file tool.",
    )

    print(f"Agent response:\n{result.final_output}\n")

    inner = sandbox_agent.agent
    print(f"SandboxAgent configuration:")
    print(f"  Name: {inner.name}")
    print(f"  Model: {inner.model}")
    entries = list(sandbox_agent.manifest.entries.keys())
    print(f"  Manifest entries: {entries}")
    tool_names = [t.name for t in inner.tools]
    print(f"  Tools: {tool_names}")

    print("\n=== Sandbox Agent Demo Complete ===")
    print(
        "With gpt-5.5+, use Capabilities.default() for built-in shell"
        "\nand filesystem tools instead of custom function tools."
    )


if __name__ == "__main__":
    asyncio.run(main())
