import os
import asyncio

from google.adk import Agent
from google.adk.planners import PlanReActPlanner, BuiltInPlanner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from settings import settings

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- PlanReActPlanner for explicit plan-then-act reasoning
- BuiltInPlanner for Gemini's native planning capability
- Comparing agent behavior with and without planners
- Planning for multi-step tool-use tasks

ADK v2.0 introduced planners that make agents think before acting.
PlanReActPlanner generates an explicit plan as a first step, then
executes it. BuiltInPlanner uses Gemini's native planning mode
for more efficient built-in reasoning.

For more details, visit:
https://google.github.io/adk-docs/agents/planners/
-------------------------------------------------------
"""

APP_NAME = "planner_demo"
USER_ID = "user"


# --- Tools for the agent ---
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    weather_data = {
        "London": "cloudy, 14°C, 70% humidity",
        "Paris": "sunny, 22°C, 40% humidity",
        "Tokyo": "rainy, 18°C, 85% humidity",
        "New York": "clear, 25°C, 50% humidity",
    }
    return weather_data.get(city, f"No weather data available for {city}")


def get_flights(origin: str, destination: str) -> str:
    """Get available flights between two cities."""
    return f"Flight from {origin} to {destination}: $450, departing 9:00 AM, arriving 2:00 PM"


def get_hotels(city: str, budget: str) -> str:
    """Get hotel recommendations for a city within a budget."""
    return f"Hotel in {city} ({budget} budget): Grand Hotel, $150/night, 4.5 stars"


# --- 1. Agent with PlanReActPlanner ---
planning_agent = Agent(
    name="travel_planner",
    model=settings.GOOGLE_MODEL_NAME,
    instruction="""You are a travel planning assistant. Help users plan trips
    by checking weather, finding flights, and recommending hotels.
    Break complex requests into steps and execute them systematically.""",
    tools=[get_weather, get_flights, get_hotels],
    planner=PlanReActPlanner(),
)

# --- 2. Same agent without planner (for comparison) ---
basic_agent = Agent(
    name="travel_basic",
    model=settings.GOOGLE_MODEL_NAME,
    instruction="""You are a travel planning assistant. Help users plan trips
    by checking weather, finding flights, and recommending hotels.""",
    tools=[get_weather, get_flights, get_hotels],
)


async def run_agent(agent: Agent, query: str, label: str):
    """Run an agent and print results."""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    print(f"\n{'=' * 50}")
    print(f"=== {label} ===")
    print(f"{'=' * 50}")
    print(f"Query: {query}\n")

    user_message = Content(
        role="user",
        parts=[Part(text=query)],
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=user_message,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text and part.text.strip():
                    print(f"[{event.author}]: {part.text.strip()[:300]}")


async def main():
    query = "I want to travel from London to Tokyo. Check the weather in Tokyo, find me a flight, and suggest a mid-range hotel."

    # Run with PlanReActPlanner (generates explicit plan first)
    await run_agent(planning_agent, query, "With PlanReActPlanner")

    # Run without planner (direct execution)
    await run_agent(basic_agent, query, "Without Planner (baseline)")

    print("\n\n=== Planner Comparison ===")
    print("PlanReActPlanner: Generates an explicit plan, then executes step by step")
    print("BuiltInPlanner:   Uses Gemini's native planning (more efficient)")
    print("No planner:       Agent decides on the fly (may miss steps)")


if __name__ == "__main__":
    asyncio.run(main())
