from typing import Any

from strands import Agent, tool
from strands.models.openai import OpenAIModel
from strands.vended_interventions.hitl import HumanInTheLoop

from settings import settings

"""
-------------------------------------------------------
In this example, we explore Strands Agents SDK with the following features:
- HumanInTheLoop, the vended approval intervention (new in v1.44.0)
- allowed_tools to let read-only tools run without approval
- The interrupt/resume loop: stop_reason == "interrupt" -> result.interrupts
- Resuming with an interruptResponse content block, and a custom async ask callback

By default HumanInTheLoop pauses the agent before every tool call and returns
an interrupt instead of blocking, so the approval can be routed anywhere — a
web UI, a Slack message, a ticket. Passing ask="stdio" prompts on the terminal
instead, and passing an async callable lets you await your own approval service.

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/agents/interventions/human-in-the-loop/
-------------------------------------------------------
"""


# --- 1. Define one read-only tool and one that needs approval ---
@tool
def get_balance(account: str) -> str:
    """Read the current balance of an account.

    Args:
        account: Account identifier.
    """
    return f"{account} balance: $2,400.00"


@tool
def transfer_funds(account: str, amount: float) -> str:
    """Move money out of an account.

    Args:
        account: Account to debit.
        amount: Amount in dollars.
    """
    return f"transferred ${amount:.2f} from {account}"


openai_model = OpenAIModel(
    client_args={
        "api_key": settings.OPENAI_API_KEY.get_secret_value()
        if settings.OPENAI_API_KEY
        else ""
    },
    model_id=settings.OPENAI_MODEL_NAME,
)


def build_agent(hitl: HumanInTheLoop) -> Agent:
    """Create a banking agent guarded by the given approval handler."""
    return Agent(
        model=openai_model,
        system_prompt=(
            "You are a banking assistant. Use the tools. Answer in one short sentence. "
            "If a tool call was blocked, say plainly that it did not run."
        ),
        tools=[get_balance, transfer_funds],
        interventions=[hitl],
        callback_handler=None,
    )


print("=== Human-in-the-Loop: Interrupt and Resume ===\n")

# --- 2. Allow-listed tools run freely, no approval needed ---
agent = build_agent(HumanInTheLoop(allowed_tools=["get_balance"]))

print("--- Allow-listed tool: no pause ---")
result = agent("What is the balance of account ACC-1?")
print(f"stop_reason: {result.stop_reason}")
print(f"Agent: {result.message['content'][0]['text']}\n")

# --- 3. Any other tool pauses the agent with an interrupt ---
print("--- Guarded tool: agent pauses ---")
result = agent("Transfer $500 from account ACC-1.")
print(f"stop_reason: {result.stop_reason}")

interrupt = result.interrupts[0]
print(f"interrupt id: {interrupt.id}")
print(f"interrupt reason: {interrupt.reason}\n")

# --- 4. Resume with an approval ---
print("--- Resume with 'yes' ---")
result = agent(
    [{"interruptResponse": {"interruptId": interrupt.id, "response": "yes"}}]
)
print(f"stop_reason: {result.stop_reason}")
print(f"Agent: {result.message['content'][0]['text']}\n")

# --- 5. Resume with a rejection — the tool never runs ---
print("--- Resume with 'no' ---")
deny_agent = build_agent(HumanInTheLoop(allowed_tools=["get_balance"]))
result = deny_agent("Transfer $9000 from account ACC-1.")
print(f"stop_reason: {result.stop_reason}")
interrupt = result.interrupts[0]
result = deny_agent(
    [{"interruptResponse": {"interruptId": interrupt.id, "response": "no"}}]
)
print("transfer_funds never ran — the model got a CONFIRMATION_FAILED tool result")
print(f"Agent: {result.message['content'][0]['text']}\n")


# --- 6. Inline approval with a custom async ask callback ---
async def policy_service_ask(prompt: str, **kwargs: Any) -> str:
    """Approve transfers under $1000 without pausing the agent."""
    approved = "9000" not in prompt
    print(f"  [policy-service] {'approved' if approved else 'rejected'}: {prompt}")
    return "yes" if approved else "no"


print("--- Inline approval with a custom async ask ---")
inline_agent = build_agent(HumanInTheLoop(ask=policy_service_ask))
result = inline_agent("Transfer $250 from account ACC-2.")
print(f"stop_reason: {result.stop_reason}")
print(f"Agent: {result.message['content'][0]['text']}\n")

# --- 7. Summary ---
print("--- Summary ---")
print("HumanInTheLoop modes:")
print("  ask=None (default) -> returns an interrupt; resume from anywhere")
print("  ask='stdio'        -> prompts y/n on the terminal (interactive CLI only)")
print("  ask=<async fn>     -> awaits your own approval service inline")
print("allowed_tools whitelists safe tools; '!tool' forces approval even if trusted.")
