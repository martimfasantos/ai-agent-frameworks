import asyncio

from dotenv import load_dotenv

from claude_agent_sdk import (
    query,
    ResultMessage,
    ClaudeAgentOptions,
    SandboxSettings,
    SandboxNetworkConfig,
)

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Claude Agent SDK with the following features:
- SandboxSettings for agent execution sandboxing
- SandboxNetworkConfig for controlling network access
- Restricting which domains sandboxed bash commands can reach
- Running agents in constrained environments

Sandbox settings (SDK 0.2.x) let you control how Claude sandboxes
bash commands during execution. This is important for:
- Running untrusted prompts safely
- Preventing data exfiltration via network
- Limiting which domains commands can reach
- Production security hardening

For more details, visit:
https://platform.claude.com/docs/en/agent-sdk/configuration
-------------------------------------------------------
"""


async def main():
    # ------------------------------------------------------------------
    # Example 1: Sandboxed bash with all outbound domains denied
    # ------------------------------------------------------------------
    print("=== Example 1: Sandbox with Network Locked Down ===")

    async for message in query(
        prompt="What is 15 * 23? Calculate without using any tools.",
        options=ClaudeAgentOptions(
            sandbox=SandboxSettings(
                enabled=True,  # Enable bash sandboxing
                network=SandboxNetworkConfig(
                    allowedDomains=[],  # No outbound domains allowed
                ),
            ),
            max_turns=1,
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"Response: {message.result[:200]}")
    print()

    # ------------------------------------------------------------------
    # Example 2: Sandboxed bash with a domain whitelist
    # ------------------------------------------------------------------
    print("=== Example 2: Full Sandbox Configuration ===")

    async for message in query(
        prompt="List the files in the current directory.",
        options=ClaudeAgentOptions(
            sandbox=SandboxSettings(
                enabled=True,
                network=SandboxNetworkConfig(
                    allowedDomains=["api.github.com"],  # Whitelist
                ),
            ),
            max_turns=2,
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"Response: {message.result[:300]}")

    print("\n=== Sandbox Settings Summary ===")
    print("enabled=True:           Sandbox bash commands (macOS/Linux)")
    print("network.allowedDomains: Whitelist outbound domains ([] blocks all)")
    print("network.deniedDomains:  Always-blocked domains")
    print("Sandboxing prevents data exfiltration and limits blast radius")


if __name__ == "__main__":
    asyncio.run(main())
