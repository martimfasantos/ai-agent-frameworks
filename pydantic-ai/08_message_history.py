from dotenv import load_dotenv
from pydantic_ai import (
    Agent,
    ModelRequest,
    ModelResponse,
    RequestUsage,
    RunContext,
    ModelMessage,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.capabilities import ProcessHistory
from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_core import to_json

from utils import print_all_messages
from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Multi-turn conversations with persistent message history
- Accessing and inspecting message history from agent results
- JSON serialization and deserialization of conversation history
- The ProcessHistory capability for filtering and managing message content
- Context preservation across multiple agent interactions

This example demonstrates how to manage conversation history and context with Pydantic AI.
Message history enables multi-turn conversations where the agent remembers previous
interactions, creating more natural and contextual dialogue experiences. The example
shows how to persist conversations across sessions using JSON serialization and how
to filter message content using history processors, making it essential for building
conversational AI applications like chatbots, virtual assistants, and any system
requiring contextual understanding across interactions.

For more details, visit:
https://pydantic.dev/docs/ai/core-concepts/message-history/
-----------------------------------------------------------------------
"""


# --- 1. Define History Processors ---
# 1.1 Simple history processor example
async def keep_recent_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
    """Keep only the last 2 messages to manage token usage."""
    return messages[-2:] if len(messages) > 2 else messages


# 1.2 Context-aware history processor example
def context_aware_processor(
    ctx: RunContext,
    messages: list[ModelMessage],
) -> list[ModelMessage]:
    # Access current usage
    current_tokens = ctx.usage.total_tokens

    # Filter messages based on context
    if current_tokens > 1000:
        return messages[-3:]  # Keep only recent messages when token usage is high

    else:
        return [
            msg for msg in messages if isinstance(msg, ModelRequest)
        ]  # Keep only user requests otherwise


# --- 2. Agents with the ProcessHistory capability ---
history_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions="You are a helpful assistant",
    capabilities=[ProcessHistory(keep_recent_messages)],  # can add more than one
)

context_aware_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions="You are a helpful assistant",
    capabilities=[ProcessHistory(context_aware_processor)],
)

# --- 3. Run Examples ---
if __name__ == "__main__":
    print("=== Basic Conversation ===")

    # Message history
    message_history = [
        ModelRequest(  # this will be filtered out by history processor
            parts=[
                SystemPromptPart(content="Be a helpful assistant."),
                UserPromptPart(content="Tell me a joke."),
            ],
        ),
        ModelResponse(
            parts=[
                TextPart(
                    content="Did you hear about the toothpaste scandal? They called it Colgate."
                )
            ],
            usage=RequestUsage(input_tokens=60, output_tokens=12),
            model_name=settings.OPENAI_MODEL_NAME,
        ),
    ]

    # Third interaction building on context
    result1 = history_agent.run_sync("Explain", message_history=message_history)
    print(f"Response: {result1.output}")

    print("\n=== Message Inspection ===")
    all_messages = result1.all_messages()
    print(f"Total messages in conversation: {len(all_messages)}")
    print_all_messages(all_messages)

    print("\n=== Storing and Loading Messages ===")

    # Serialize messages to JSON
    messages_json = to_json(result1.all_messages())
    print(f"Serialized {len(messages_json)} bytes to JSON")

    # Load messages from JSON
    loaded_messages = ModelMessagesTypeAdapter.validate_json(messages_json)
    print(f"Loaded {len(loaded_messages)} messages from JSON")

    # Use loaded messages in new conversation with history agent
    result4 = history_agent.run_sync(
        "What did we discuss?", message_history=loaded_messages
    )
    print(f"Response of History Agent using loaded history: {result4.output}")

    # Use loaded messages in new conversation with context-aware agent
    result4 = context_aware_agent.run_sync(
        "What's Portugal known for?",
        message_history=loaded_messages,
        # Loaded messages are not taken into account in this agent
        # because they have the id of the previous agent
    )

    print(f"\n=== New History after Context-Aware Processing ===")
    filtered_messages = result4.all_messages()
    print_all_messages(filtered_messages)
    # > This should filter all the ModelResponse messages from the history
    # > and only show the ModelResponse for the last interaction.
