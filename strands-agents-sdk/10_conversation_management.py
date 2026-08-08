from strands import Agent
from strands.agent.conversation_manager import (
    NullConversationManager,
    SlidingWindowConversationManager,
    SummarizingConversationManager,
)
from strands.models.openai import OpenAIModel

from settings import settings

"""
-------------------------------------------------------
In this example, we explore Strands Agents SDK with the following features:
- NullConversationManager (no history management)
- SlidingWindowConversationManager (fixed window of recent turns)
- SummarizingConversationManager (auto-summarize older context)
- pin_first=N to protect the first N messages from truncation (new in v1.43.0)

Conversation managers control how the agent's message history grows.
The default SlidingWindowConversationManager keeps a fixed window of
recent messages. SummarizingConversationManager compresses older turns
into a summary. NullConversationManager disables all history management.
pin_first is available on both managers and keeps early instructions or
reference data in context no matter how long the conversation gets.

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/agents/conversation-management/
-------------------------------------------------------
"""

# Configure the model (default: Agent() uses Amazon Bedrock with AWS credentials)
openai_model = OpenAIModel(
    client_args={
        "api_key": settings.OPENAI_API_KEY.get_secret_value()
        if settings.OPENAI_API_KEY
        else ""
    },
    model_id=settings.OPENAI_MODEL_NAME,
)

# --------------------------------------------------------------
# Example 1: SlidingWindowConversationManager (default)
# --------------------------------------------------------------
print("=== Example 1: Sliding Window (default) ===\n")

# --- 1. Create agent with sliding window manager ---
sliding_agent = Agent(
    model=openai_model,
    system_prompt="You are a helpful assistant. Be concise.",
    conversation_manager=SlidingWindowConversationManager(
        window_size=5,
        should_truncate_results=True,
    ),
    callback_handler=None,
)

# --- 2. Simulate a multi-turn conversation ---
sliding_agent("My name is Alice.")
sliding_agent("I live in Portland.")
sliding_agent("I work as a data scientist.")
result = sliding_agent("What do you know about me? Summarize in one sentence.")
print(f"Sliding window result: {result.message}")
print(f"Messages in history: {len(sliding_agent.messages)}\n")

# --------------------------------------------------------------
# Example 2: NullConversationManager (no management)
# --------------------------------------------------------------
print("=== Example 2: NullConversationManager ===\n")

# --- 3. Create agent with null manager ---
null_agent = Agent(
    model=openai_model,
    system_prompt="You are a helpful assistant. Be concise.",
    conversation_manager=NullConversationManager(),
    callback_handler=None,
)

null_agent("My name is Bob.")
result = null_agent("What is my name?")
print(f"Null manager result: {result.message}")
print(f"Messages in history: {len(null_agent.messages)}\n")

# --------------------------------------------------------------
# Example 3: SummarizingConversationManager
# --------------------------------------------------------------
print("=== Example 3: SummarizingConversationManager ===\n")

# --- 4. Create agent with summarizing manager ---
summarizing_agent = Agent(
    model=openai_model,
    system_prompt="You are a helpful assistant. Be concise.",
    conversation_manager=SummarizingConversationManager(
        summary_ratio=0.5,
        preserve_recent_messages=2,
    ),
    callback_handler=None,
)

# --- 5. Build up history that may trigger summarization ---
summarizing_agent("The capital of France is Paris.")
summarizing_agent("The capital of Germany is Berlin.")
summarizing_agent("The capital of Japan is Tokyo.")
summarizing_agent("The capital of Brazil is Brasilia.")
result = summarizing_agent("List all the capitals I mentioned.")
print(f"Summarizing result: {result.message}")
print(f"Messages in history: {len(summarizing_agent.messages)}\n")

# --------------------------------------------------------------
# Example 4: pin_first — protecting early messages from truncation
# --------------------------------------------------------------
print("=== Example 4: pin_first ===\n")

# --- 6. A tight window that would normally drop the opening instruction ---
pinned_agent = Agent(
    model=openai_model,
    system_prompt="You are a helpful assistant. Be concise.",
    conversation_manager=SlidingWindowConversationManager(
        window_size=6,
        pin_first=1,  # the first message is never truncated away
    ),
    callback_handler=None,
)

pinned_agent("Our project code name is FALCON-9. Remember it.")
pinned_agent("What is 2 + 2?")
pinned_agent("Name a colour.")
pinned_agent("Name a fruit.")
result = pinned_agent("What is our project code name?")

# --- 7. The pinned opening message survived the sliding window ---
first_message = pinned_agent.messages[0]["content"][0]["text"]
print(f"Messages in history: {len(pinned_agent.messages)} (window_size=6)")
print(f"Message[0] still pinned: {first_message!r}")
print(f"Recall result: {result.message['content'][0]['text']}")
