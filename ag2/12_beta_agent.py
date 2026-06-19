import asyncio
import os

from autogen.beta import Agent
from autogen.beta.config import OpenAIConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2's Beta Agent with the following features:
- The new beta Agent class (autogen.beta.Agent)
- OpenAIConfig for model configuration
- Async-first design with agent.ask()
- AgentReply with .body for response text

AG2 v0.12+ introduces a new beta Agent that will become the
official API at v1.0. It uses an async-first design, typed
configuration objects, and a simplified ask() interface
compared to the classic ConversableAgent.

For more details, visit:
https://docs.ag2.ai/latest/docs/user-guide/release-roadmap/
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
