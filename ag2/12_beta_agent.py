import asyncio
import os

from ag2 import Agent
from ag2.config import OpenAIConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2's Agent with the following features:
- The Agent class, promoted from autogen.beta to top-level ag2
- OpenAIConfig for model configuration
- Async-first design with agent.ask()
- AgentReply with .body for response text

These examples were written against the v0.12 beta Agent. At v1.0
that beta was promoted to the official API: the import path moved
from autogen.beta to ag2, and every call below is unchanged.

For more details, visit:
https://docs.ag2.ai/latest/docs/beta/agents/
-------------------------------------------------------
"""


async def main() -> None:
    agent = Agent(
        "assistant",
        "You are a helpful assistant. Be concise, reply in 1-2 sentences.",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
    )

    print("=== Beta Agent: Simple Question ===\n")
    reply = await agent.ask("Where does the phrase 'hello world' come from?")
    print(f"Response: {reply.body}")

    print("\n=== Beta Agent: Second Question ===\n")
    reply2 = await agent.ask("What is the capital of Portugal?")
    print(f"Response: {reply2.body}")

    print("\n=== Reply History ===")
    events = list(await reply2.history.get_events())
    print(f"  Events in history: {len(events)}")
    for event in events:
        print(f"  - {type(event).__name__}")


if __name__ == "__main__":
    asyncio.run(main())
