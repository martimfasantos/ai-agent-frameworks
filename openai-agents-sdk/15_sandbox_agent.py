"""
-------------------------------------------------------
In this example, we explore OpenAI Agents SDK with the following features:
- SandboxAgent with a Manifest of workspace files
- Capabilities.default() — built-in filesystem, shell and compaction tools
- Running the sandbox on UnixLocalSandboxClient via RunConfig(sandbox=...)

A SandboxAgent runs inside an isolated workspace. Its Manifest declares the
files to stage, and Capabilities give the model real shell and filesystem
tools instead of hand-written ones. Runtime transport (which sandbox client,
which session) is supplied per run through `RunConfig(sandbox=...)`.

NOTE: Sandbox Capabilities are Responses-API-only and need a GPT-5.5+ model,
so this example hardcodes `gpt-5.6` instead of using
`settings.OPENAI_MODEL_NAME` (gpt-4o-mini rejects the sandbox tools).

For more details, visit:
https://openai.github.io/openai-agents-python/sandbox_agents/
-------------------------------------------------------
"""

import asyncio
import json
import os

from agents import RunConfig, Runner, ToolCallItem, ToolCallOutputItem
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Capabilities
from agents.sandbox.entries import File
from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient

from settings import settings

# ---------------------------------------------------------------------------
# 0. Env setup
# ---------------------------------------------------------------------------
os.environ.setdefault("OPENAI_API_KEY", settings.OPENAI_API_KEY.get_secret_value())

SANDBOX_MODEL = "gpt-5.6"

# ---------------------------------------------------------------------------
# 1. Workspace files to stage into the sandbox
# ---------------------------------------------------------------------------
HELLO_PY = '''\
def greet(name: str = "World") -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"


def shout(name: str) -> str:
    """Return a greeting in upper case."""
    return greet(name).upper()


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
# 2. Build a SandboxAgent with a Manifest and built-in capabilities
# ---------------------------------------------------------------------------
def build_sandbox_agent() -> SandboxAgent:
    """Create a SandboxAgent that reviews the code staged in its workspace."""

    # Manifest entries are typed workspace entries (File, Dir, LocalFile, mounts, ...).
    manifest = Manifest(
        entries={
            "hello.py": File(content=HELLO_PY.encode()),
            "task.md": File(content=TASK_MD.encode()),
        }
    )

    return SandboxAgent(
        name="Code Reviewer",
        model=SANDBOX_MODEL,
        instructions=(
            "You are a code reviewer working inside a sandbox workspace. "
            "Read the files you need with your filesystem and shell tools, "
            "then answer in a few short lines."
        ),
        default_manifest=manifest,
        capabilities=Capabilities.default(),
    )


# ---------------------------------------------------------------------------
# 3. Run the sandbox agent
# ---------------------------------------------------------------------------
async def main() -> None:
    print("=== Sandbox Agent Example ===\n")

    sandbox_agent = build_sandbox_agent()

    print("SandboxAgent configuration:")
    print(f"  Name: {sandbox_agent.name}")
    print(f"  Model: {sandbox_agent.model}")
    print(f"  Manifest entries: {list(sandbox_agent.default_manifest.entries)}")
    print(f"  Capabilities: {[c.type for c in sandbox_agent.capabilities]}")
    print("  Client: UnixLocalSandboxClient\n")

    print("Running the agent in the sandbox...\n")
    result = await Runner.run(
        sandbox_agent,
        input="Read task.md and follow its instructions.",
        # Transport lives on the run, not on the agent.
        run_config=RunConfig(sandbox=SandboxRunConfig(client=UnixLocalSandboxClient())),
    )

    # --- 4. Show the sandbox commands the model actually ran ---
    print("Sandbox tool activity:")
    for item in result.new_items:
        if isinstance(item, ToolCallItem):
            args = json.loads(item.raw_item.arguments or "{}")
            print(f"  -> {item.raw_item.name}: {args.get('cmd', args)}")
            if "workdir" in args:
                print(f"     workspace: {args['workdir']}")
        elif isinstance(item, ToolCallOutputItem):
            for line in str(item.output).splitlines():
                if line.startswith("Process exited"):
                    print(f"     {line}")

    print(f"\nAgent response:\n{result.final_output}")

    print("\n=== Sandbox Agent Demo Complete ===")
    print("The files were staged from the Manifest and read with real shell tools.")


if __name__ == "__main__":
    asyncio.run(main())
