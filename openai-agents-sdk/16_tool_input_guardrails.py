import os
import json
import asyncio

from agents import (
    Agent,
    Runner,
    function_tool,
    ToolInputGuardrailData,
    ToolGuardrailFunctionOutput,
    ToolInputGuardrailTripwireTriggered,
    tool_input_guardrail,
)
from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------------------------
In this example, we explore OpenAI's Agent class with the following features:
- Tool input guardrails (added in openai-agents 0.17.6)

Tool input guardrails run *before* a tool is executed, letting you inspect
the arguments the model wants to pass and decide what should happen. Each
guardrail returns a ToolGuardrailFunctionOutput with one of three behaviors:
- allow:          run the tool normally (default)
- reject_content: skip the tool and feed a message back to the model so it
                  can recover, without ever executing the tool
- raise_exception: halt the run by raising ToolInputGuardrailTripwireTriggered

Unlike input/output guardrails (which guard the agent), tool input guardrails
guard a specific tool call. Here we protect a money-transfer tool: small
amounts are allowed, mid-size amounts are softly rejected back to the model,
and oversized amounts hard-stop the run.
-------------------------------------------------------------------------
"""

# 1. Define a tool input guardrail. It receives a single ToolInputGuardrailData
#    object; the raw JSON arguments live in data.context.tool_call.arguments.
@tool_input_guardrail
def transfer_amount_guard(
    data: ToolInputGuardrailData,
) -> ToolGuardrailFunctionOutput:
    raw_args = data.context.tool_call.arguments
    try:
        amount = float(json.loads(raw_args).get("amount", 0))
    except (json.JSONDecodeError, TypeError, ValueError):
        amount = 0.0

    if amount > 10_000:
        # Hard stop: raise ToolInputGuardrailTripwireTriggered.
        return ToolGuardrailFunctionOutput.raise_exception(
            output_info={"amount": amount, "decision": "blocked"}
        )

    if amount > 1_000:
        # Soft reject: the tool is skipped and the model is told why.
        return ToolGuardrailFunctionOutput.reject_content(
            message=(
                f"Transfers over $1,000 require human approval. "
                f"Refused to transfer ${amount:,.2f}."
            ),
            output_info={"amount": amount, "decision": "rejected"},
        )

    return ToolGuardrailFunctionOutput.allow(
        output_info={"amount": amount, "decision": "allowed"}
    )


# 2. Attach the guardrail to a tool via tool_input_guardrails.
@function_tool(tool_input_guardrails=[transfer_amount_guard])
def transfer_money(recipient: str, amount: float) -> str:
    """Transfer money to a recipient.

    Args:
        recipient: The name of the person receiving the money.
        amount: The amount of money to transfer, in US dollars.
    """
    return f"Transferred ${amount:,.2f} to {recipient}."


# 3. Define the agent with the guarded tool.
agent = Agent(
    name="Banking Assistant",
    instructions=(
        "You are a banking assistant. Use the transfer_money tool to carry out "
        "transfers the user requests. Report the outcome plainly."
    ),
    model=settings.OPENAI_MODEL_NAME,
    tools=[transfer_money],
)


async def main():

    # 4. Small amount: the guardrail allows the tool to run.
    result = await Runner.run(agent, "Please transfer $50 to Alice.")
    print("Allowed case:")
    print(result.final_output)

    # 5. Mid-size amount: the guardrail rejects the content, and the model
    #    explains the refusal instead of moving the money.
    result = await Runner.run(agent, "Please transfer $5,000 to Bob.")
    print("\nRejected case:")
    print(result.final_output)

    # 6. Oversized amount: the guardrail raises and halts the run.
    try:
        await Runner.run(agent, "Please transfer $25,000 to Carol.")
        print("\nBlocked case: guardrail did not trip - this is unexpected.")
    except ToolInputGuardrailTripwireTriggered as e:
        print("\nBlocked case: guardrail tripped.")
        print(f"Info: {e.output.output_info}")


if __name__ == "__main__":
    asyncio.run(main())
