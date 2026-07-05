from dotenv import load_dotenv

from deepagents import create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Defining custom Python functions as tools
- Passing tools to the agent via the tools= parameter
- Letting the agent decide when to call a tool

Tools are plain Python functions with type hints and a docstring. The
docstring becomes the tool's description that the model reads to decide
when (and how) to call it. Here we give the agent a mock weather tool so
it can answer questions it otherwise couldn't.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/tools
-----------------------------------------------------------------------
"""


# --- 1. Define custom tools ---
def get_weather(city: str) -> str:
    """Get the current weather report for a given city."""
    print(f"[tool] get_weather called with city={city!r}")
    fake_weather = {
        "lisbon": "sunny, 25°C",
        "london": "rainy, 14°C",
        "tokyo": "cloudy, 19°C",
    }
    return fake_weather.get(city.lower(), f"No data for {city}")


# --- 2. Create the agent with the tool ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    tools=[get_weather],
    system_prompt="You are a helpful assistant. Use tools when needed and reply in one sentence.",
)

# --- 3. Invoke the agent ---
print("=== Deep Agents Tools ===")
question = "What's the weather like in Lisbon and Tokyo?"
result = agent.invoke({"messages": [{"role": "user", "content": question}]})

# --- 4. Print the final answer ---
print(f"\nUser: {question}")
print(f"Agent: {result['messages'][-1].text}")
