import asyncio
import os
import shutil

from ag2 import Agent
from ag2.acp import ClaudeCodeConfig, CodexConfig, OpenCodeConfig
from ag2.events import ModelMessageChunk, ModelReasoning
from ag2.events.tool_events import BuiltinToolCallEvent

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- ag2.acp configs driving external CLI coding agents
- An ACP-backed Agent using the same ask() / run() API
- Streaming the CLI agent's thoughts and tool calls as AG2 events

The Agent Client Protocol lets AG2 drive Claude Code, Codex or
OpenCode as ordinary agents: the config IS the model config, so no
Agent API changes. Everything the CLI agent does is externalised
onto AG2's event stream, so it can be observed and gated like any
other agent.

This example needs a CLI agent binary on PATH and an authenticated
session for it. When none is available it verifies construction and
reports that plainly rather than pretending to have run.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/cli_agents.mdx
-------------------------------------------------------
"""

# --- 1. Each adapter is a preset with its own launch command ---
ADAPTERS = {
    "Claude Code": ClaudeCodeConfig,
    "Codex": CodexConfig,
    "OpenCode": OpenCodeConfig,
}


def observe(event: object) -> None:
    """Render the CLI agent's work as it streams in."""
    if isinstance(event, ModelReasoning):
        print(f"  [thinking] {event.content}")
    elif isinstance(event, BuiltinToolCallEvent):
        print(f"  [tool] {event.name}({event.arguments})")
    elif isinstance(event, ModelMessageChunk):
        print(event.content, end="", flush=True)


async def main() -> None:
    os.makedirs("res/acp_workspace", exist_ok=True)

    # --- 2. Show each preset's launch command and whether it is available ---
    print("=== ACP adapters ===\n")
    available: list[tuple[str, type]] = []
    for label, config_cls in ADAPTERS.items():
        command = config_cls().command
        found = shutil.which(command[0])
        print(f"  {label:<12} command={' '.join(command):<20} on PATH={bool(found)}")
        if found:
            available.append((label, config_cls))

    # --- 3. Construct an ACP-backed Agent (works with or without the binary) ---
    config = ClaudeCodeConfig(cwd="res/acp_workspace", permission_policy="auto")
    agent = Agent("coder", config=config)
    print("\n=== Agent construction ===")
    print(f"  agent name:        {agent.name}")
    print(f"  config type:       {type(config).__name__}")
    print(f"  workspace (cwd):   {config.cwd}")
    print(f"  permission_policy: {config.permission_policy}")
    print(f"  expose_tools:      {config.expose_tools}")

    if not available:
        print("\n=== Skipped: no CLI agent binary on PATH ===")
        print("  Install one of the commands above, authenticate it, and rerun.")
        return

    # --- 4. Drive the first available CLI agent for one prompt turn ---
    label, config_cls = available[0]
    print(f"\n=== Driving {label} ===\n")
    try:
        async with config_cls(
            cwd="res/acp_workspace", permission_policy="auto", turn_timeout=120.0
        ) as live_config:
            live_agent = Agent("coder", config=live_config)
            async with live_agent.run(
                "Create hello.txt containing the single word 'hello'."
            ) as run:
                run.stream.subscribe(observe)
                reply = await run.result()
        print(f"\n{label}: {reply.body}")
    except Exception as error:
        print(f"  {label} session failed: {type(error).__name__}: {error}")
        print("  This usually means the CLI agent is installed but not authenticated.")


if __name__ == "__main__":
    asyncio.run(main())
