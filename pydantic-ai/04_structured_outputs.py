from dotenv import load_dotenv
from pydantic import BaseModel

from pydantic_ai import Agent, ToolOutput, NativeOutput, PromptedOutput

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Pydantic model outputs with automatic validation
- Different output modes: Tool, Native, and Prompted
- Union types for multiple output format options
- Complex nested models with validation rules
- Output type flexibility and runtime type checking

This example demonstrates how to generate structured, 
validated outputs using Pydantic AI. Instead of plain text responses, 
agents can return structured data as Pydantic models, ensuring type 
safety and automatic validation of AI-generated content. 

The example shows different output modes (Tool, Native, Prompted) 
and how to handle multiple output types with union types.

For more details, visit:
https://pydantic.dev/docs/ai/core-concepts/output/
-----------------------------------------------------------------------
"""


# --- 1. Basic Structured Output ---
class CityLocation(BaseModel):
    city: str
    country: str


basic_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=CityLocation,  # structured output type
    instructions="Extract city and country information",
)


# --- 2. Multiple Output Types ---
class Person(BaseModel):
    name: str
    age: int


class Animal(BaseModel):
    species: str
    habitat: str


# Agent that can return either a Person or Animal
union_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=[Person, Animal],  # Union of types
    instructions="Extract either person or animal information from the text",
)

# --- 3. Different Output Modes ---
# reference: https://pydantic.dev/docs/ai/core-concepts/output/#output-modes

# Tool Output (default) - uses function calling to format output
tool_output_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=ToolOutput(Person, name="extract_person"),
    instructions="Extract person information using tool output",
)

# Native Output - uses model's native structured output (aka "JSON Schema response format")
native_output_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=NativeOutput(Person, name="PersonData"),
    instructions="Extract person information using native output",
)

# Prompted Output - passed in the prompt to the model to match the provided JSON schema
prompted_output_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=PromptedOutput(Person, name="PersonInfo"),
    instructions="Extract person information using prompted output",
)

# --- 4. Run Examples ---
if __name__ == "__main__":
    print("=== Basic Structured Output ===")
    result1 = basic_agent.run_sync("Where were the 2012 Olympics held?")
    print(f"Output: {result1.output}")
    print(f"Type: {type(result1.output)}")

    print("\n=== Union Types ===")
    result2 = union_agent.run_sync("John is 25 years old and works as a teacher")
    print(f"Person Output: {result2.output}")

    result3 = union_agent.run_sync("Lions live in the African savanna")
    print(f"Animal Output: {result3.output}")

    print("\n=== Tool Output Mode ===")
    result4 = tool_output_agent.run_sync("Sarah is a 30-year-old doctor")
    print(f"Tool Output: {result4.output}")

    print("\n=== Native Output Mode ===")
    result5 = native_output_agent.run_sync("Mike is a 28-year-old engineer")
    print(f"Native Output: {result5.output}")

    print("\n=== Prompted Output Mode ===")
    result6 = prompted_output_agent.run_sync("Lisa is a 35-year-old artist")
    print(f"Prompted Output: {result6.output}")
