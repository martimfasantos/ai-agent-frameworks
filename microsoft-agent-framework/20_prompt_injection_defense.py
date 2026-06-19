import asyncio
import warnings

from dotenv import load_dotenv

from agent_framework import Agent, tool
from agent_framework.openai import OpenAIChatClient
from agent_framework.security import (
    SecureAgentConfig,
    IntegrityLabel,
    ConfidentialityLabel,
)

from settings import settings

load_dotenv()

# Suppress experimental warnings for cleaner output
warnings.filterwarnings("ignore", message=".*experimental.*")
warnings.filterwarnings("ignore", message=".*ExperimentalWarning.*")

"""
-------------------------------------------------------
In this example, we explore Microsoft Agent Framework
with the following features:
- Information-flow control (FIDES) for prompt injection defense
- Integrity labels to track trust levels of content
- Confidentiality labels to prevent data exfiltration
- SecureAgentConfig for policy enforcement

FIDES (Faithful Integrity Defense for Enterprise Security)
applies information-flow control to agent execution. It tags
content with integrity labels (trusted vs untrusted) and
confidentiality labels (public vs private), then enforces
policies that prevent untrusted content from influencing
sensitive operations or private data from leaking out.

For more details, visit:
https://github.com/microsoft/agent-framework/pull/5331
-------------------------------------------------------
"""


# --- 1. Define tools ---
@tool(name="read_public_data", description="Read publicly available data")
def read_public_data(topic: str) -> str:
    """Returns public information about a topic."""
    data = {
        "weather": "Current weather: Sunny, 22C in Lisbon",
        "news": "Top headline: AI agents framework reaches v1.3",
    }
    return data.get(topic.lower(), f"No public data for '{topic}'")


@tool(name="read_internal_data", description="Read internal company data")
def read_internal_data(department: str) -> str:
    """Returns internal data (would be marked PRIVATE in production)."""
    data = {
        "finance": "Q2 Revenue: $4.2M",
        "hr": "Headcount plan: +15 engineers",
    }
    return data.get(department.lower(), f"No data for '{department}'")


async def main() -> None:
    # --- 2. Create the client ---
    client = OpenAIChatClient(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    # --- 3. Show available labels ---
    print("=== FIDES Information-Flow Control Labels ===")
    print()
    print("Integrity Labels (trust level of content):")
    for label in IntegrityLabel:
        print(f"  - {label.name}: {label.value}")
    print()
    print("Confidentiality Labels (visibility level):")
    for label in ConfidentialityLabel:
        print(f"  - {label.name}: {label.value}")
    print()

    # --- 4. Create a SecureAgentConfig ---
    config = SecureAgentConfig(
        default_integrity=IntegrityLabel.UNTRUSTED,
        default_confidentiality=ConfidentialityLabel.PUBLIC,
        block_on_violation=True,
        enable_audit_log=True,
    )
    print("=== SecureAgentConfig ===")
    print(f"  source_id:                {config.source_id}")
    print(f"  policy_enforcement:       {config.enable_policy_enforcement}")
    print(f"  label_tracker available:  {config.label_tracker is not None}")
    print(f"  policy_enforcer available: {config.policy_enforcer is not None}")
    print()

    # --- 5. Run agent with tools ---
    agent = client.as_agent(
        name="assistant",
        instructions="You are a helpful assistant. Be concise, reply in 1-2 sentences.",
        tools=[read_public_data, read_internal_data],
    )

    print("=== Agent Response (tools available) ===")
    result = await agent.run("What's the weather like?")
    print(f"  Response: {result.text}")
    print()

    # --- 6. Summary ---
    print("=== Summary ===")
    print("FIDES enables tagging agent content with integrity and")
    print("confidentiality labels to enforce data-flow policies:")
    print("  - UNTRUSTED inputs cannot influence sensitive tool calls")
    print("  - PRIVATE data cannot leak to public-facing outputs")
    print("  - Violations can be blocked or routed to approval flows")
    print("  - Full audit logging tracks all policy decisions")


if __name__ == "__main__":
    asyncio.run(main())
