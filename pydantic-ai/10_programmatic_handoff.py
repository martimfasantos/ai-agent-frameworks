import asyncio
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from pydantic_ai import Agent, ModelMessage, RunUsage, UsageLimits

from utils import show_metrics
from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Multi-Agent Applications patterns
- Multiple agents called in succession by application code (not via tools)
- Passing message history between agent runs for context continuity
- Shared usage tracking across multiple agent runs
- Application code orchestrates which agent runs next

Programmatic hand-off differs from agent delegation by having application code
control the workflow rather than agents calling each other. Each specialized
agent runs independently, and the application passes context via message history
between runs. This is useful when the orchestration logic is deterministic.

For more details, visit:
https://pydantic.dev/docs/ai/guides/multi-agent-applications/#programmatic-agent-hand-off
-----------------------------------------------------------------------
"""


# --- 1. Define output models ---
class FlightDetails(BaseModel):
    flight_number: str
    origin: str
    destination: str


class SeatPreference(BaseModel):
    row: int = Field(ge=1, le=30)
    seat: Literal["A", "B", "C", "D", "E", "F"]


class Failed(BaseModel):
    """Unable to find a satisfactory choice."""

    reason: str = ""


# --- 2. Create flight search agent ---
flight_search_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=FlightDetails | Failed,
    system_prompt=(
        "Use the flight_search tool to find a flight "
        "from the given origin to the given destination."
    ),
)


@flight_search_agent.tool_plain
def flight_search(origin: str, destination: str) -> str:
    """Search for available flights between two cities.

    Args:
        origin: Departure city.
        destination: Arrival city.
    """
    # Simulated flight search
    return f"Found flight AK456 from {origin} to {destination}, departing 14:30."


# --- 3. Create seat preference agent ---
seat_preference_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=SeatPreference | Failed,
    system_prompt=(
        "Extract the user's seat preference. "
        "Seats A and F are window seats. "
        "Row 1 is the front row and has extra leg room. "
        "Rows 14 and 20 also have extra leg room."
    ),
)


# --- 4. Run the sequential workflow ---
async def main():
    print("=== Programmatic Hand-Off Example ===\n")

    # Create shared usage tracker for all agent runs
    usage = RunUsage()
    usage_limits = UsageLimits(request_limit=5)

    # Step 1: Find a flight using the flight search agent
    print("Step 1: Flight Search")
    print("=" * 60)

    flight_result = await flight_search_agent.run(
        "Find me a flight from Lisbon to London",
        usage=usage,
        usage_limits=usage_limits,
    )

    if isinstance(flight_result.output, Failed):
        print(f"Flight search failed: {flight_result.output.reason}")
        return

    flight = flight_result.output
    print(
        f"Flight found: {flight.flight_number} ({flight.origin} -> {flight.destination})"
    )

    # Capture message history from first agent run
    flight_messages: list[ModelMessage] = flight_result.all_messages()
    print(f"Messages from flight agent: {len(flight_messages)}")
    print()

    # Step 2: Get seat preference using the seat agent
    # Pass message_history so the seat agent has context about the booking
    print("Step 2: Seat Selection")
    print("=" * 60)

    seat_result = await seat_preference_agent.run(
        "I'd like a window seat with extra leg room please",
        message_history=flight_messages,  # Context continuity
        usage=usage,  # Same shared usage tracker
        usage_limits=usage_limits,
    )

    if isinstance(seat_result.output, Failed):
        print(f"Seat selection failed: {seat_result.output.reason}")
        return

    seat = seat_result.output
    print(f"Seat selected: Row {seat.row}, Seat {seat.seat}")
    print()

    # Step 3: Summary
    print("Step 3: Booking Summary")
    print("=" * 60)
    print(f"  Flight: {flight.flight_number}")
    print(f"  Route:  {flight.origin} -> {flight.destination}")
    print(f"  Seat:   Row {seat.row}, Seat {seat.seat}")

    # Show combined metrics — usage was shared across both agents
    show_metrics(usage)


if __name__ == "__main__":
    asyncio.run(main())
