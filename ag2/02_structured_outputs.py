import asyncio
import os

from pydantic import BaseModel

from ag2 import Agent
from ag2.config import OpenAIConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- Structured output via the Agent response_schema= parameter
- Parsing the typed value with await reply.content()
- Overriding the schema for a single turn on ask()

response_schema constrains the model's final message to a schema
and reply.content() returns the parsed Python object, so agent
output is safe to feed straight into downstream code without any
manual JSON handling. reply.body still holds the raw model text.

For more details, visit:
https://docs.ag2.ai/latest/docs/beta/structured_output/
-------------------------------------------------------
"""


# --- 1. Define the Pydantic output models ---
class CityInfo(BaseModel):
    name: str
    country: str
    population: str
    famous_for: str
    best_time_to_visit: str


class Distance(BaseModel):
    from_city: str
    to_city: str
    kilometres: int


async def main() -> None:
    # --- 2. Create an agent bound to a schema ---
    agent = Agent(
        "city_expert",
        prompt="You are a city information expert. Provide accurate structured data.",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        response_schema=CityInfo,
    )

    # --- 3. Ask and parse the typed result ---
    print("=== Structured output: CityInfo ===\n")
    reply = await agent.ask("Tell me about Tokyo.")
    city = await reply.content()

    print(f"  raw body:           {reply.body}")
    print(f"  parsed type:        {type(city).__name__}")
    print(f"  City:               {city.name}")
    print(f"  Country:            {city.country}")
    print(f"  Population:         {city.population}")
    print(f"  Famous for:         {city.famous_for}")
    print(f"  Best time to visit: {city.best_time_to_visit}")

    # --- 4. Override the schema for one turn only ---
    print("\n=== Per-turn schema override: Distance ===\n")
    reply2 = await agent.ask(
        "How far is Tokyo from Lisbon?",
        response_schema=Distance,
    )
    distance = await reply2.content()
    print(f"  parsed type: {type(distance).__name__}")
    print(f"  {distance.from_city} -> {distance.to_city}: {distance.kilometres} km")


if __name__ == "__main__":
    asyncio.run(main())
