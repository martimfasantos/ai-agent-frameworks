import os

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore LangChain with the following features:
- Human-in-the-Loop middleware for tool approval
- Interrupt-based execution pausing
- Resuming with approve/reject decisions

Human-in-the-Loop (HITL) adds human oversight to agent tool calls.
When the agent proposes a sensitive action, execution pauses via
an interrupt. A human can then approve, edit, or reject the action
before the agent continues. This requires a checkpointer to persist
state across the interrupt.

For more details, visit:
https://docs.langchain.com/oss/python/langchain/human-in-the-loop
-------------------------------------------------------
"""


# --- 1. Define tools (safe and sensitive) ---
@tool
def search_docs(query: str) -> str:
    """Search documentation for information. This is a safe operation."""
    docs = {
        "refund": "Refund policy: items can be returned within 30 days.",
        "shipping": "Standard shipping takes 3-5 business days.",
    }
    for key, value in docs.items():
        if key in query.lower():
            return value
    return f"No docs found for: {query}"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient. This is a sensitive operation."""
    return f"Email sent to {to} with subject '{subject}'"


@tool
def delete_account(user_id: str) -> str:
    """Delete a user account. This is a destructive operation."""
    return f"Account {user_id} has been deleted"


# --- 2. Create the model ---
model = ChatOpenAI(model=settings.OPENAI_MODEL_NAME)

# --- 3. Create agent with HITL middleware ---
agent = create_agent(
    model=model,
    tools=[search_docs, send_email, delete_account],
    system_prompt="You are a support assistant. Use tools to help the user.",
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "search_docs": False,  # Auto-approve safe operations
                # `when` is a predicate over the tool call: only external
                # recipients need approval, internal mail is auto-approved
                "send_email": InterruptOnConfig(
                    allowed_decisions=["approve", "edit", "reject"],
                    when=lambda request: not request.tool_call["args"]["to"].endswith(
                        "@acme.com"
                    ),
                ),
                "delete_account": {  # Only approve or reject (no editing)
                    "allowed_decisions": ["approve", "reject"],
                },
            },
        ),
    ],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "hitl-demo"}}

# --- 4. Trigger an interrupt by requesting a sensitive action ---
print("=== Requesting email send (will interrupt) ===")
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Send an email to alice@example.com about the refund policy",
            }
        ]
    },
    config=config,
    version="v2",
)

# Check if there are interrupts
if result.interrupts:
    interrupt = result.interrupts[0]
    print(f"Interrupt received!")
    print(f"  Action requests: {interrupt.value.get('action_requests', [])}")

    # --- 5. Resume with approval ---
    print("\n=== Approving the action ===")
    final_result = agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=config,
        version="v2",
    )
    print(f"Final response: {final_result.value['messages'][-1].content}")
else:
    print(f"No interrupt (auto-approved): {result.value['messages'][-1].content}")

# --- 6. The same tool skips the interrupt when `when` returns False ---
print("\n=== Requesting email to an internal address (when -> False) ===")
internal_result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Send an email to bob@acme.com about the shipping policy",
            }
        ]
    },
    config={"configurable": {"thread_id": "hitl-internal"}},
    version="v2",
)
print(f"Interrupts raised: {len(internal_result.interrupts)}")
print(f"Final response: {internal_result.value['messages'][-1].content}")
