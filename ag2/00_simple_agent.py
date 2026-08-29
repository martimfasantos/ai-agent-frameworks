import asyncio
import os

from ag2 import Agent
from ag2.config import OpenAIConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore AG2 with the following features:
- Creating an Agent with a typed OpenAIConfig
- The async-only ask() entry point and AgentReply.body
- Continuing the same conversation with AgentReply.ask()

Agent is the single core primitive in AG2 1.0. Every turn is
async: agent.ask() starts a conversation and returns an
AgentReply, and reply.ask() continues that exact conversation
with its history intact.

For more details, visit:
https://docs.ag2.ai/latest/docs/beta/agents/
-------------------------------------------------------
"""


async def main() -> None:
    # --- 1. Create the agent ---
    agent = Agent(
        "assistant",
        prompt="You are a helpful assistant. Be concise, reply in 1-2 sentences.",
        config=OpenAIConfig(model=settings.OPENAI_MODEL_NAME),
    )

    # --- 2. Start a conversation ---
    print("=== Turn 1: new conversation ===")
    reply = await agent.ask("Where does the phrase 'hello world' come from?")
    print(f"Response: {reply.body}")

    # --- 3. Continue the SAME conversation (history is carried over) ---
    print("\n=== Turn 2: continuation via reply.ask() ===")
    follow_up = await reply.ask("Now say that in five words or fewer.")
    print(f"Response: {follow_up.body}")

    # --- 4. Inspect the conversation history recorded on the stream ---
    events = await follow_up.context.stream.history.get_events()
    print(f"\n=== Conversation history: {len(events)} event(s) ===")
    for event in events:
        print(f"  - {type(event).__name__}")


if __name__ == "__main__":
    asyncio.run(main())
