from dotenv import load_dotenv
from pydantic import BaseModel, Field

from deepagents import create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Structured output via the response_format= parameter
- Defining the output schema with a Pydantic model
- Reading the parsed object back from result["structured_response"]

Instead of returning free-form text, an agent can return a typed object
that matches a schema you define. Pass a Pydantic model to
response_format and the harness coerces the final answer into that shape,
so downstream code can rely on well-typed fields instead of parsing
prose. Here we extract structured contact details from a messy sentence.

For more details, visit:
https://docs.langchain.com/oss/python/langchain/structured-output
-----------------------------------------------------------------------
"""


# --- 1. Define the output schema ---
class ContactInfo(BaseModel):
    """Structured contact details extracted from text."""

    name: str = Field(description="The person's full name")
    email: str = Field(description="The person's email address")
    company: str = Field(description="The company the person works for")


# --- 2. Create the agent with a response format ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    system_prompt="Extract the requested contact details from the user's text.",
    response_format=ContactInfo,
)

# --- 3. Invoke with unstructured text ---
print("=== Deep Agents Structured Output ===")
text = "Hey, I'm Ada Lovelace from Analytical Engines Inc. You can reach me at ada@analyticalengines.io."
result = agent.invoke({"messages": [{"role": "user", "content": text}]})

# --- 4. Read the typed object back ---
info: ContactInfo = result["structured_response"]
print(f"\nInput text: {text}\n")
print("Parsed ContactInfo object:")
print(f"  name    = {info.name!r}")
print(f"  email   = {info.email!r}")
print(f"  company = {info.company!r}")
print(f"\nType: {type(info).__name__}")
