import asyncio
import os

from pydantic import BaseModel

from autogen.beta import Agent
from autogen.beta.config import OpenAIConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2's Beta Agent with the following features:
- Structured output using response_schema with Pydantic models
- Typed responses from the beta Agent

For more details, visit:
https://docs.ag2.ai/latest/docs/user-guide/release-roadmap/
-------------------------------------------------------
"""


class CityInfo(BaseModel):
    name: str
    country: str
    population: str
    famous_for: str
    best_time_to_visit: str


async def main() -> None:
    agent = Agent(
        "city_expert",
        "You are a city information expert. Provide accurate structured data.",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
        response_schema=CityInfo,
    )

    print("=== Beta Agent: Structured Output ===\n")
    reply = await agent.ask("Tell me about Lisbon.")

    city = CityInfo.model_validate_json(reply.body)
    print(f"  City: {city.name}")
    print(f"  Country: {city.country}")
    print(f"  Population: {city.population}")
    print(f"  Famous for: {city.famous_for}")
    print(f"  Best time to visit: {city.best_time_to_visit}")

    print("\n--- Second Query ---\n")
    reply2 = await agent.ask("Tell me about Tokyo.")
    city2 = CityInfo.model_validate_json(reply2.body)
    print(f"  City: {city2.name}")
    print(f"  Country: {city2.country}")
    print(f"  Population: {city2.population}")
    print(f"  Famous for: {city2.famous_for}")
    print(f"  Best time to visit: {city2.best_time_to_visit}")


if __name__ == "__main__":
    asyncio.run(main())
