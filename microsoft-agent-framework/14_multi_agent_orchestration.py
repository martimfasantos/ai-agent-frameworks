import asyncio

from dotenv import load_dotenv

from agent_framework import Agent, Message, WorkflowRunResult
from agent_framework.openai import OpenAIChatClient
from agent_framework_orchestrations import SequentialBuilder, HandoffBuilder

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Microsoft Agent Framework
with the following features:
- Sequential orchestration (agents run in order)
- Handoff orchestration (agents transfer control)
- Using orchestration builders to compose multi-agent workflows

Orchestrations provide pre-built patterns for coordinating
multiple agents. Sequential runs agents one after another,
passing output forward. Handoff lets agents dynamically
transfer control to the most appropriate specialist.

For more details, visit:
https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/?pivots=programming-language-python
-------------------------------------------------------
"""


# --- 1. Define specialist tools ---
def search_flights(destination: str) -> str:
    """Searches for available flights to a destination."""
    flights = {
        "lisbon": "TAP TP1234: NYC->LIS, $450, 7h direct",
        "tokyo": "ANA NH109: NYC->NRT, $890, 14h direct",
    }
    return flights.get(destination.lower(), f"No flights found to {destination}.")


def search_hotels(destination: str) -> str:
    """Searches for hotels in a destination."""
    hotels = {
        "lisbon": "Hotel Avenida Palace: $180/night, 4-star, city center",
        "tokyo": "Park Hyatt Tokyo: $350/night, 5-star, Shinjuku",
    }
    return hotels.get(destination.lower(), f"No hotels found in {destination}.")


async def main() -> None:
    client = OpenAIChatClient(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    # --------------------------------------------------------------
    # Example 1: Sequential Orchestration
    # --------------------------------------------------------------
    print("=== Example 1: Sequential Orchestration ===\n")

    # --- 2. Create specialist agents ---
    researcher = client.as_agent(
        name="researcher",
        instructions=(
            "You are a travel researcher. Summarize the destination's highlights "
            "in 2-3 sentences. Pass your findings along."
        ),
    )

    planner = client.as_agent(
        name="planner",
        instructions=(
            "You are a travel planner. Based on the research provided, "
            "create a brief 3-day itinerary outline. Be concise."
        ),
    )

    # --- 3. Build and run a sequential orchestration ---
    # output_from="all" is required to see every stage: since orchestrations
    # 1.0.x the default yields only the last participant's response.
    sequential = SequentialBuilder(
        participants=[researcher, planner], output_from="all"
    ).build()

    result: WorkflowRunResult = await sequential.run("Plan a trip to Lisbon, Portugal.")

    # One AgentResponse per participant, in pipeline order.
    outputs = result.get_outputs()
    stage_names = ["Researcher", "Planner"]
    for i, output in enumerate(outputs):
        label = stage_names[i] if i < len(stage_names) else f"Stage {i + 1}"
        print(f"{label}:\n{output.text}\n")

    # --------------------------------------------------------------
    # Example 2: Handoff Orchestration
    # --------------------------------------------------------------
    print("=== Example 2: Handoff Orchestration ===\n")

    # --- 4. Create agents with tools for handoff ---
    flight_agent = client.as_agent(
        name="flight-agent",
        description="Specialist for finding flights",
        instructions="You find flights. Use your search_flights tool and report results concisely.",
        tools=[search_flights],
        require_per_service_call_history_persistence=True,
    )

    hotel_agent = client.as_agent(
        name="hotel-agent",
        description="Specialist for finding hotels",
        instructions="You find hotels. Use your search_hotels tool and report results concisely.",
        tools=[search_hotels],
        require_per_service_call_history_persistence=True,
    )

    triage = client.as_agent(
        name="triage-agent",
        description="Routes requests to the right specialist",
        instructions=(
            "You are a triage agent. Determine what the user needs and "
            "hand off to the appropriate specialist."
        ),
        require_per_service_call_history_persistence=True,
    )

    # --- 5. Build and run a handoff orchestration ---
    handoff = (
        HandoffBuilder(participants=[flight_agent, hotel_agent, triage])
        .with_start_agent(triage)
        .build()
    )

    result = await handoff.run("I need a hotel in Tokyo.")

    # Handoff outputs are AgentResponse objects — the triage agent's
    # output is typically empty (it just routes), while the specialist
    # agent provides the actual answer.
    outputs = result.get_outputs()
    for output in outputs:
        text = output.text if hasattr(output, "text") else str(output)
        if text:
            print(f"Output: {text}\n")


if __name__ == "__main__":
    asyncio.run(main())
