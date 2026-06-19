import os
import asyncio

from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from settings import settings

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- Agent transfer control with disallow_transfer_to_parent
- Agent transfer control with disallow_transfer_to_peers
- Restricting agent routing to enforce strict workflows
- Combining transfer controls for one-way agent pipelines

In ADK v2.0, agents can transfer control to parent or peer agents
by default. The new disallow_transfer_to_parent and
disallow_transfer_to_peers parameters let you restrict these
transfers, which is useful for:
- Preventing loops in multi-agent conversations
- Enforcing one-way handoffs (e.g., triage -> specialist)
- Creating "terminal" agents that must complete their task

For more details, visit:
https://google.github.io/adk-docs/agents/multi-agents/
-------------------------------------------------------
"""

APP_NAME = "transfer_control_demo"
USER_ID = "user"
SESSION_ID = "session-001"


# --- 1. Specialist agents with restricted transfers ---

# This agent cannot transfer back to the parent (triage) agent.
# Once the user is routed here, this agent must handle the request.
billing_agent = Agent(
    name="billing_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction="""You are a billing specialist. Help the user with
    invoices, payments, and subscription questions.
    Always provide a helpful answer about billing.""",
    disallow_transfer_to_parent=True,  # Cannot send user back to triage
    disallow_transfer_to_peers=True,   # Cannot transfer to other specialists
)

# This agent can transfer back to parent but not to peers.
technical_agent = Agent(
    name="technical_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction="""You are a technical support specialist. Help the user
    with technical issues, bugs, and configuration problems.
    If you cannot help, you may escalate back.""",
    disallow_transfer_to_parent=False,  # Can escalate back to triage
    disallow_transfer_to_peers=True,    # Cannot transfer directly to billing
)

# --- 2. Triage agent (root) that routes to specialists ---

triage_agent = Agent(
    name="triage_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction="""You are a customer support triage agent.
    Route billing questions to billing_agent.
    Route technical questions to technical_agent.
    For general questions, answer directly.""",
    sub_agents=[billing_agent, technical_agent],
)


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    runner = Runner(
        agent=triage_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # --- Example: Billing question (one-way transfer) ---
    print("=== User asks a billing question ===")
    user_message = Content(
        role="user",
        parts=[Part(text="I need help with my last invoice, it seems wrong.")],
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=user_message,
    ):
        if event.content and event.content.parts:
            agent_name = event.author or "unknown"
            text = event.content.parts[0].text
            if text and text.strip():
                print(f"[{agent_name}]: {text.strip()}")

    print("\n=== Transfer control summary ===")
    print("billing_agent:   disallow_transfer_to_parent=True,  disallow_transfer_to_peers=True")
    print("                 -> Terminal agent, must handle request fully")
    print("technical_agent: disallow_transfer_to_parent=False, disallow_transfer_to_peers=True")
    print("                 -> Can escalate back to triage, but not to billing")


if __name__ == "__main__":
    asyncio.run(main())
