import asyncio
import json

from dotenv import load_dotenv

from agent_framework import Agent, ClassSkill, SkillsProvider
from agent_framework.openai import OpenAIChatClient

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Microsoft Agent Framework
with the following features:
- ClassSkill for class-based skill definitions
- @ClassSkill.resource for declarative data resources
- @ClassSkill.script for callable skill scripts
- SkillsProvider for injecting skills into agents

ClassSkill lets you package related resources and scripts
into a reusable Python class. The agent reads resources
for reference data and calls scripts to perform actions,
keeping domain logic self-contained and testable.

For more details, visit:
https://learn.microsoft.com/en-us/agent-framework/agents/skills
-------------------------------------------------------
"""


# --- 1. Define a ClassSkill ---
class UnitConverterSkill(ClassSkill):
    """A skill that converts between measurement units."""

    def __init__(self) -> None:
        super().__init__(
            name="unit-converter",
            description="Convert between common measurement units.",
        )

    @property
    def instructions(self) -> str:
        return (
            "Use this skill to convert values between units. "
            "First read the conversion-table resource to find the factor, "
            "then call the convert script with the value and factor."
        )

    @ClassSkill.resource(name="conversion-table")
    def get_conversion_table(self) -> str:
        """Returns a table of conversion factors."""
        return (
            "| From     | To         | Factor    |\n"
            "|----------|------------|-----------|\n"
            "| miles    | km         | 1.60934   |\n"
            "| kg       | lbs        | 2.20462   |\n"
            "| celsius  | fahrenheit | *1.8+32   |\n"
            "| liters   | gallons    | 0.264172  |"
        )

    @ClassSkill.script(name="convert")
    def convert(self, value: float, factor: float, offset: float = 0.0) -> str:
        """Converts a value using: result = value * factor + offset."""
        result = round(value * factor + offset, 4)
        return json.dumps({"input": value, "factor": factor, "offset": offset, "result": result})


async def main() -> None:
    # --- 2. Create the client and agent with the skill ---
    client = OpenAIChatClient(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )

    skill = UnitConverterSkill()
    skills_provider = SkillsProvider(source=skill)

    agent = Agent(
        client=client,
        name="converter",
        instructions="You are a unit conversion assistant. Use your skill to convert units. Be concise, reply in 1-2 sentences.",
        context_providers=[skills_provider],
    )

    # --- 3. Run the agent with conversion queries ---
    print("=== ClassSkill: Unit Converter ===")

    result = await agent.run("Convert 26.2 miles to kilometers.")
    print(f"Query: Convert 26.2 miles to km")
    print(f"Answer: {result.text}")
    print()

    result = await agent.run("How many pounds is 75 kg?")
    print(f"Query: How many pounds is 75 kg?")
    print(f"Answer: {result.text}")

    # --- 4. Show skill metadata ---
    print(f"\nSkill name: {skill.name}")
    print(f"Skill description: {skill.description}")
    print(f"Resources: {[r.name for r in skill.resources]}")
    print(f"Scripts: {[s.name for s in skill.scripts]}")


if __name__ == "__main__":
    asyncio.run(main())
