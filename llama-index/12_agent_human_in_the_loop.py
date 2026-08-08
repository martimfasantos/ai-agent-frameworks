import asyncio

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import (
    Context,
    HumanResponseEvent,
    InputRequiredEvent,
)
from llama_index.llms.openai import OpenAI

from settings import settings


"""
-------------------------------------------------------
In this example, we explore LlamaIndex with the following features:
- Agent-level human-in-the-loop from inside a tool
- ctx.wait_for_event() to suspend a tool until a human replies
- waiter_event to tell the caller what input is needed
- requirements={...} to route a reply to the right pending question
- handler.ctx.send_event() to deliver the answer programmatically

Some tools must not run unattended — a deploy, a refund, a delete. Instead of
approving the whole agent run up front, the tool itself calls
ctx.wait_for_event(): the agent pauses, the waiter_event surfaces on the event
stream, and the tool resumes with the human's answer as its return value. The
`requirements` dict filters incoming HumanResponseEvents so two concurrent
questions cannot get each other's answers.

Approvals here are decided by a lookup table rather than stdin, so the example
runs unattended.

For more details, visit:
https://developers.llamaindex.ai/python/framework/understanding/agent/human_in_the_loop/
-------------------------------------------------------
"""

# --- 1. Approvals a real deployment would ask a human for ---
APPROVALS = {"staging": "yes", "production": "no"}


# --- 2. A tool that blocks on human confirmation ---
async def deploy(ctx: Context, environment: str) -> str:
    """Deploy the application to the given environment. Requires human approval."""
    question = f"Deploy to {environment}? (yes/no) "

    # Suspend here. waiter_event is what the caller sees; requirements makes sure
    # only a HumanResponseEvent tagged with this environment wakes us up.
    response = await ctx.wait_for_event(
        HumanResponseEvent,
        waiter_id=question,
        waiter_event=InputRequiredEvent(prefix=question, environment=environment),
        requirements={"environment": environment},
        timeout=60,
    )

    if response.response.strip().lower() == "yes":
        return f"Deployed to {environment}."
    return f"Deployment to {environment} was rejected by the operator."


# --- 3. Create the agent with the approval-gated tool ---
agent = FunctionAgent(
    name="deploy_agent",
    description="Deploys applications after human approval.",
    system_prompt=(
        "You deploy applications with the deploy tool. Call it once per "
        "environment requested, then report the outcome of each in one line."
    ),
    tools=[deploy],
    llm=OpenAI(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    ),
)


# --- 4. Drive the approvals from the event stream ---
async def main():
    handler = agent.run("Deploy to staging and then to production.")

    async for event in handler.stream_events():
        if isinstance(event, InputRequiredEvent):
            answer = APPROVALS.get(event.environment, "no")
            print(f"[human] {event.prefix}-> {answer}")

            # The requirements filter on the tool side matches on this field
            handler.ctx.send_event(
                HumanResponseEvent(response=answer, environment=event.environment)
            )

    print(f"\nAgent: {await handler}")


if __name__ == "__main__":
    asyncio.run(main())
