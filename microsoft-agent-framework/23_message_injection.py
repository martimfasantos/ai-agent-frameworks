import asyncio
from typing import Annotated

from dotenv import load_dotenv

from agent_framework import (
    MESSAGE_INJECTION_PENDING_MESSAGES_STATE_KEY,
    Agent,
    AgentSession,
    MessageInjectionMiddleware,
    enqueue_messages,
    tool,
)
from agent_framework.openai import OpenAIChatClient

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Microsoft Agent Framework
with the following features:
- MessageInjectionMiddleware for mid-turn message delivery
- enqueue_messages(session, ...) to nudge a running agent
- Draining queued messages into the next model call

Normally a new user message means a new agent run. With this
middleware, a message enqueued while the agent is still working —
here, while a slow tool awaits — is drained into the *same* turn's
next model call, so the final answer accounts for it. That is how
you support "wait, one more thing" without cancelling and restarting.

For more details, visit:
https://learn.microsoft.com/en-us/agent-framework/agents/middleware/
-------------------------------------------------------
"""

TOOL_DURATION_SECONDS = 6
INJECT_AFTER_SECONDS = 2


# --- 1. A deliberately slow tool, so there is a window to inject into ---
# approval_mode="never_require" keeps the demo unattended; see example 10
# for the approval-gated pattern.
@tool(approval_mode="never_require")
async def check_inventory(
    item: Annotated[str, "The item to check stock for."],
) -> str:
    """Looks up warehouse stock for an item."""
    print(f"[tool] checking inventory for {item!r}...")
    await asyncio.sleep(TOOL_DURATION_SECONDS)
    print("[tool] inventory lookup finished")
    return f"{item}: 4 in stock, curbside pickup available today."


def pending_count(session: AgentSession) -> int:
    """Number of messages still waiting to be drained into the next model call."""
    state = session.to_dict().get("state", {})
    return len(state.get(MESSAGE_INJECTION_PENDING_MESSAGES_STATE_KEY, []))


async def main() -> None:
    client = OpenAIChatClient(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    # --- 2. The middleware owns the pending-message queue on the session ---
    agent = Agent(
        client=client,
        name="inventory-agent",
        instructions=(
            "You answer store inventory questions. Always call check_inventory "
            "before answering. If another user message arrives before you have "
            "answered, address it in the same final answer. Be concise."
        ),
        tools=check_inventory,
        middleware=[MessageInjectionMiddleware()],
    )
    session = AgentSession()

    # --- 3. Start the run without awaiting it, so we keep control ---
    question = "Can I pick up a red travel mug today? Check inventory first."
    print("=== Message Injection ===")
    print(f"User: {question}")
    run_task = asyncio.ensure_future(agent.run(question, session=session))

    # --- 4. While the tool is still sleeping, enqueue a follow-up ---
    await asyncio.sleep(INJECT_AFTER_SECONDS)
    follow_up = "Actually I can only collect it after 5 PM — is that fine?"
    print(f"User (injected mid-turn): {follow_up}")
    enqueue_messages(session, follow_up)
    print(f"Pending messages queued while the run is in flight: {pending_count(session)}")

    # --- 5. The same run's final model call sees tool result + injection ---
    result = await run_task
    print(f"\nAgent: {result.text}")

    # --- 6. The middleware drained the queue inside that single run ---
    print(f"\nPending messages after the run: {pending_count(session)}")
    print("Agent runs started: 1 (the follow-up never needed its own turn)")


if __name__ == "__main__":
    asyncio.run(main())
