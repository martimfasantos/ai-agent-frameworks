import os
from agents import Agent, Runner
from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore a simple Hello World agent
-------------------------------------------------------
"""

# 1. Define the agent
agent = Agent(
    name="Assistant", 
    instructions="You are a helpful assistant", # this is the system prompt
    model=settings.OPENAI_MODEL_NAME,  # specify the model to use (default: "gpt-4o")
)

# 2. Run the agent with a user message
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# 3. Since 0.19.0, SDK config objects can also be passed as plain dicts and are
#    coerced at the input boundary (unknown fields raise TypeError).
dict_agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model=settings.OPENAI_MODEL_NAME,
    model_settings={"temperature": 0.2},  # instead of ModelSettings(temperature=0.2)
)
print(
    f"\nmodel_settings dict coerced to "
    f"{type(dict_agent.model_settings).__name__}"
    f"(temperature={dict_agent.model_settings.temperature})"
)