import os

from pydantic import BaseModel, Field, model_validator

from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy, ToolStrategy
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore LangChain with the following features:
- ToolStrategy vs ProviderStrategy, the two ways to produce structured output
- A union schema, letting the model choose between an answer and a refusal shape
- ToolStrategy(tool_message_content=) to control what the model sees after answering
- ToolStrategy(handle_errors=) to feed validation failures back for a retry
- ProviderStrategy(strict=) for provider-side schema enforcement

Passing a bare Pydantic class to response_format lets LangChain pick a strategy
for you. Naming the strategy is what you want in production: ToolStrategy works
with any tool-calling model and can retry on validation errors, while
ProviderStrategy pushes the schema to the provider's own structured-output API
so invalid JSON is never generated in the first place.

For more details, visit:
https://docs.langchain.com/oss/python/langchain/structured-output
-------------------------------------------------------
"""

model = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=0)


# --- 1. A tool backing the answers ---
@tool
def lookup_weather(city: str) -> str:
    """Look up today's weather for a city in the weather database."""
    data = {"lisbon": "sunny, 26.0C", "london": "cloudy, 15.0C"}
    return data.get(city.lower(), f"'{city}' is not in the weather database")


# --------------------------------------------------------------
# Example 1: ToolStrategy with a union schema
# --------------------------------------------------------------
print("=== Example 1: ToolStrategy with a union schema ===")


# --- 2. Two response shapes, one per outcome ---
class WeatherReport(BaseModel):
    """A weather answer backed by the weather database."""

    city: str = Field(description="The city that was looked up")
    conditions: str = Field(description="Short description of the conditions")
    temperature_c: float = Field(description="Temperature in degrees Celsius")


class OutOfScope(BaseModel):
    """Returned when the question cannot be answered from the weather database."""

    reason: str = Field(description="Why the question cannot be answered")
    suggestion: str = Field(description="What the user should ask instead")


# --- 3. The union is passed straight to ToolStrategy ---
union_agent = create_agent(
    model=model,
    tools=[lookup_weather],
    response_format=ToolStrategy(
        schema=WeatherReport | OutOfScope,
        tool_message_content="Structured answer recorded.",
    ),
    system_prompt="You are a weather desk. Only answer from the weather database.",
)

for question in ["What is the weather in Lisbon?", "Who won the 1998 World Cup?"]:
    result = union_agent.invoke({"messages": [{"role": "user", "content": question}]})
    answer = result["structured_response"]
    print(f"  Q: {question}")
    print(f"    schema chosen: {type(answer).__name__}")
    print(f"    fields       : {answer.model_dump()}")

# The synthetic structured-output tool call gets this content instead of a JSON echo.
last_tool_message = [m for m in result["messages"] if m.type == "tool"][-1]
print(f"  tool_message_content in history: {last_tool_message.content!r}\n")

# --------------------------------------------------------------
# Example 2: ToolStrategy(handle_errors=) retrying a validation failure
# --------------------------------------------------------------
print("=== Example 2: ToolStrategy retrying on a validation error ===")

validation_attempts = {"count": 0}


# --- 4. A schema that rejects its first attempt, to make the retry path visible ---
class VerifiedReport(BaseModel):
    """A weather answer that must pass an extra verification step."""

    city: str = Field(description="The city that was looked up")
    temperature_c: float = Field(description="Temperature in degrees Celsius")

    @model_validator(mode="after")
    def reject_first_attempt(self) -> "VerifiedReport":
        validation_attempts["count"] += 1
        if validation_attempts["count"] == 1:
            raise ValueError("city must be reported as 'City, Country'")
        return self


# --- 5. handle_errors turns the exception into a retry instruction for the model ---
def on_validation_error(exc: Exception) -> str:
    print(f"  [handle_errors] caught {type(exc).__name__}, asking the model to retry")
    return f"Your structured answer was rejected: {exc}. Fix it and answer again."


retrying_agent = create_agent(
    model=model,
    tools=[lookup_weather],
    response_format=ToolStrategy(
        schema=VerifiedReport,
        handle_errors=on_validation_error,
    ),
    system_prompt="You are a weather desk. Only answer from the weather database.",
)

result = retrying_agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather in London?"}]}
)
print(f"  validation attempts: {validation_attempts['count']}")
print(f"  accepted answer    : {result['structured_response'].model_dump()}\n")

# --------------------------------------------------------------
# Example 3: ProviderStrategy with strict schema enforcement
# --------------------------------------------------------------
print("=== Example 3: ProviderStrategy(strict=True) ===")


# --- 6. The provider validates the schema, so no retry loop is needed ---
class CityFacts(BaseModel):
    """Structured facts about a city."""

    name: str = Field(description="City name")
    country: str = Field(description="Country the city is in")
    landmarks: list[str] = Field(description="Two well-known landmarks")


# strict=True is only forwarded for OpenAI-compatible models (langchain 1.3.11);
# other providers keep their own default behaviour.
provider_agent = create_agent(
    model=model,
    response_format=ProviderStrategy(schema=CityFacts, strict=True),
    system_prompt="You are a city almanac.",
)

result = provider_agent.invoke(
    {"messages": [{"role": "user", "content": "Give me facts about Lisbon."}]}
)
facts = result["structured_response"]
print(f"  {facts.name}, {facts.country}")
print(f"  landmarks: {', '.join(facts.landmarks)}")
print(f"  messages in history: {len(result['messages'])} (no structured-output tool call)")
