import asyncio
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from pydantic_ai import Agent, AgentSpec

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Defining agents declaratively via AgentSpec (YAML/JSON/dict)
- Loading an agent from a YAML string
- Saving and loading specs to/from files
- Building a runnable Agent from a spec with Agent.from_spec()

AgentSpec lets you define agent configuration (model, instructions,
model settings, capabilities, output_retries, etc.) in a declarative format
outside of Python code. This is useful for non-developer configuration,
version-controlled agent definitions, and dynamic agent loading.

For more details, visit:
https://ai.pydantic.dev/agent-spec/
-----------------------------------------------------------------------
"""


async def main():

    # ------------------------------------------------------------------
    # Example 1: Create an AgentSpec from a Python dict
    # ------------------------------------------------------------------
    print("=== Example 1: AgentSpec from Dict ===")

    spec_dict = {
        "model": settings.OPENAI_MODEL_NAME,
        "name": "dict_agent",
        "instructions": "Be concise. Reply in one sentence.",
        "output_retries": 2,
        "model_settings": {"temperature": 0.3},
    }

    spec = AgentSpec.from_dict(spec_dict)
    agent1 = Agent.from_spec(spec)
    result1 = await agent1.run("What is the capital of Portugal?")
    print(f"Response: {result1.output}\n")

    # ------------------------------------------------------------------
    # Example 2: Create an AgentSpec from a YAML string
    # ------------------------------------------------------------------
    print("=== Example 2: AgentSpec from YAML ===")

    yaml_text = f"""
model: {settings.OPENAI_MODEL_NAME}
name: yaml_agent
instructions: You are a helpful assistant that speaks like a pirate. Be concise.
output_retries: 2
model_settings:
  temperature: 0.7
"""

    spec2 = AgentSpec.from_text(yaml_text, fmt="yaml")
    agent2 = Agent.from_spec(spec2)
    result2 = await agent2.run("Tell me one fun fact about octopuses.")
    print(f"Response: {result2.output}\n")

    # ------------------------------------------------------------------
    # Example 3: Save a spec to file and reload it
    # ------------------------------------------------------------------
    print("=== Example 3: Save and Load from File ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = Path(tmpdir) / "agent_spec.yaml"

        # Save
        spec.to_file(yaml_path, schema_path=None)
        print(f"Saved spec to {yaml_path}")
        print(f"Contents:\n{yaml_path.read_text()}")

        # Reload
        loaded_spec = AgentSpec.from_file(yaml_path)
        agent3 = Agent.from_spec(loaded_spec)
        result3 = await agent3.run("What is 2 + 2?")
        print(f"Response from reloaded spec: {result3.output}\n")

    # ------------------------------------------------------------------
    # Example 4: Inspect spec fields programmatically
    # ------------------------------------------------------------------
    print("=== Example 4: Inspect Spec Fields ===")

    print(f"Name: {spec.name}")
    print(f"Model: {spec.model}")
    print(f"Output retries: {spec.output_retries}")
    print(f"Instructions: {spec.instructions}")
    print(f"Model settings: {spec.model_settings}")


if __name__ == "__main__":
    asyncio.run(main())
