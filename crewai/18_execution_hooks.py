import os

from crewai import Agent, Task, Crew
from crewai.tools import tool

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI with the following features:
- Execution hooks using @before_llm_call and @after_llm_call
- Tool call hooks using @before_tool_call and @after_tool_call
- Intercepting and logging LLM and tool interactions

Execution hooks let you intercept LLM calls and tool calls at
runtime. This is useful for logging, metrics collection, prompt
modification, or implementing custom caching strategies.

These four decorators are the legacy dialect; they are kept as adapters over
the unified interception dispatcher, which also covers the execution and step
boundaries (see 26_interception_hooks.py).

For more details, visit:
https://docs.crewai.com/en/learn/execution-hooks
-------------------------------------------------------
"""

from crewai.hooks import (
    before_llm_call,
    after_llm_call,
    before_tool_call,
    after_tool_call,
)


# --- 1. Define execution hooks ---
@before_llm_call
def log_before_llm(context):
    """Hook that runs before every LLM call."""
    print(f"[HOOK] Before LLM call - Context type: {type(context).__name__}")
    return context  # Ignored: edit context.messages in place, or return False to block


@after_llm_call
def log_after_llm(context):
    """Hook that runs after every LLM call."""
    print(f"[HOOK] After LLM call - Response received")
    return context  # Ignored: return a str to replace context.response


@before_tool_call
def log_before_tool(context):
    """Hook that runs before every tool call."""
    print(f"[HOOK] Before tool call - Context type: {type(context).__name__}")
    return context  # Ignored: edit context.tool_input in place, or return False to block


@after_tool_call
def log_after_tool(context):
    """Hook that runs after every tool call."""
    print(f"[HOOK] After tool call - Context type: {type(context).__name__}")
    return context  # Ignored: return a str to replace context.tool_result


# --- 2. Define a simple tool ---
@tool("get_temperature")
def get_temperature(city: str) -> str:
    """Gets the current temperature for a city.

    Args:
        city: The name of the city.

    Returns:
        A string with temperature information.
    """
    temperatures = {
        "lisbon": "22C sunny",
        "london": "14C cloudy",
        "tokyo": "28C humid",
    }
    return temperatures.get(city.lower(), f"No data for {city}")


# --- 3. Create agent and task ---
agent = Agent(
    role="Weather Reporter",
    goal="Report weather using available tools",
    backstory="You are a weather reporter.",
    tools=[get_temperature],
    llm=settings.OPENAI_MODEL_NAME,
    verbose=True,
)

task = Task(
    description="Get the temperature in Lisbon and write a brief weather report.",
    expected_output="A short weather report for Lisbon.",
    agent=agent,
)

# --- 4. Create and run the crew ---
crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True,
)

result = crew.kickoff()
# Hooks will print their logs during execution
print("Result:", result.raw[:300])
