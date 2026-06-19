import os

from langchain.agents import create_agent
from langchain.agents.middleware.types import (
    AgentMiddleware,
    ModelRequest,
    ToolCallRequest,
)
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore LangChain with the following features:
- Dynamic tool registration via middleware (new in v1.2.7)
- Adding tools at runtime using wrap_model_call
- Handling dynamically added tools with wrap_tool_call

Dynamic tool registration lets middleware inject tools that weren't
registered at agent creation time. The middleware overrides the model
request to include extra tools, and handles their execution via
wrap_tool_call. This is useful for plugin systems, feature flags,
or context-dependent tool availability.

For more details, visit:
https://docs.langchain.com/oss/python/langchain/middleware
-------------------------------------------------------
"""


# --- 1. Define the base tool (registered at creation) ---
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    weather_data = {
        "lisbon": "Sunny, 25C",
        "tokyo": "Cloudy, 18C",
        "new york": "Rainy, 12C",
    }
    return weather_data.get(location.lower(), f"No weather data for {location}")


# --- 2. Define a dynamic tool (NOT registered at creation) ---
@tool
def calculate_tip(bill_amount: float, tip_percentage: float = 20.0) -> str:
    """Calculate the tip amount for a restaurant bill."""
    tip = bill_amount * (tip_percentage / 100)
    return f"Tip: ${tip:.2f}, Total: ${bill_amount + tip:.2f}"


# --- 3. Create middleware that injects the dynamic tool ---
class DynamicToolMiddleware(AgentMiddleware):
    """Middleware that adds calculate_tip at runtime."""

    def wrap_model_call(self, request: ModelRequest, handler):  # type: ignore[override]
        """Inject the dynamic tool into the model's tool list."""
        updated = request.override(tools=[*request.tools, calculate_tip])
        return handler(updated)

    def wrap_tool_call(self, request: ToolCallRequest, handler):  # type: ignore[override]
        """Handle execution of the dynamically added tool."""
        if request.tool_call["name"] == "calculate_tip":
            return handler(request.override(tool=calculate_tip))
        return handler(request)


# --- 4. Create the agent with only get_weather registered ---
model = ChatOpenAI(model=settings.OPENAI_MODEL_NAME)

agent = create_agent(
    model=model,
    tools=[get_weather],  # Only base tool registered
    middleware=[DynamicToolMiddleware()],
)

# --- 5. Run a query that uses both base and dynamic tools ---
print("=== Dynamic Tool Registration ===")
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "What's the weather in Lisbon? "
                    "Also calculate a 20% tip on a $85 bill. "
                    "Be concise."
                ),
            }
        ]
    }
)
print(f"Response: {result['messages'][-1].content}")
