import asyncio
import os

from ag2 import Agent, Context, tool
from ag2.config import OpenAIConfig
from ag2.events import HumanInputRequest, HumanMessage

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- Pausing a tool for human input with await context.input()
- Registering a hitl_hook to answer HumanInputRequest events
- Gating an irreversible action behind human approval

In AG2 1.0 human-in-the-loop lives inside tools: context.input()
suspends the tool and emits a HumanInputRequest, and the agent's
hitl_hook decides how the application answers it. A real app would
block on a UI or CLI prompt here; this example answers from a
scripted queue so it runs unattended.

For more details, visit:
https://github.com/ag2ai/ag2/blob/v1.0.1/website/docs/user-guide/context/human_in_the_loop.mdx
-------------------------------------------------------
"""

# --- 1. Scripted human answers (a real app would prompt a UI) ---
SCRIPTED_ANSWERS = ["yes", "no"]
requests_seen: list[str] = []


# --- 2. A tool that will not act without human approval ---
@tool
async def book_flight(context: Context, destination: str, price_eur: int) -> str:
    """Book a flight to a destination. Requires human approval before charging."""
    answer = await context.input(
        f"Approve booking to {destination} for EUR {price_eur}? (yes/no)"
    )
    if answer.strip().lower() != "yes":
        return f"Booking to {destination} CANCELLED by the human reviewer."
    return f"Booking to {destination} CONFIRMED, charged EUR {price_eur}."


# --- 3. The hook that answers every HumanInputRequest ---
def hitl_hook(event: HumanInputRequest) -> HumanMessage:
    requests_seen.append(event.content)
    answer = SCRIPTED_ANSWERS[len(requests_seen) - 1]
    print(f"  [human] asked: {event.content}")
    print(f"  [human] answered: {answer!r}")
    return HumanMessage(content=answer)


async def main() -> None:
    agent = Agent(
        "travel_agent",
        prompt=(
            "You are a travel booking agent. Always use the book_flight tool "
            "to book. Report the tool's outcome in one sentence."
        ),
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        tools=[book_flight],
        hitl_hook=hitl_hook,
    )

    # --- 4. Approved booking ---
    print("=== Booking 1: the human approves ===")
    reply = await agent.ask("Book a flight to Barcelona for 180 euros.")
    print(f"Agent: {reply.body}\n")

    # --- 5. Rejected booking ---
    print("=== Booking 2: the human rejects ===")
    reply2 = await agent.ask("Book a flight to Reykjavik for 940 euros.")
    print(f"Agent: {reply2.body}")

    print(f"\n=== {len(requests_seen)} human input request(s) handled ===")


if __name__ == "__main__":
    asyncio.run(main())
