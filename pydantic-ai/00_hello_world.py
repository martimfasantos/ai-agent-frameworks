from dotenv import load_dotenv

from pydantic_ai import Agent

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Creating a basic Agent with a system prompt
- Synchronous execution with run_sync
- Accessing the agent's output

This is the simplest possible Pydantic AI agent. It demonstrates the
minimal setup needed to create and run an agent that responds to a
single user prompt.

For more details, visit:
https://pydantic.dev/docs/ai/core-concepts/agent/
-------------------------------------------------------
"""

# --- 1. Create the agent ---
agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions="Be concise, reply with one sentence.",
)

# --- 2. Run the agent ---
result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
