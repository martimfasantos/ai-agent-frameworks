import os

from strands import Agent
from strands.agent.conversation_manager import SummarizingConversationManager
from strands.agent.conversation_manager.conversation_manager import ProactiveCompressionConfig
from strands.handlers.callback_handler import null_callback_handler
from strands.models.openai import OpenAIModel

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore Strands Agents with the following features:
- Proactive context compression (new in v1.40.0)
- SummarizingConversationManager with ProactiveCompressionConfig
- Automatic conversation summarization to stay within token limits

Proactive compression monitors token usage during conversation
and automatically compresses older messages when a threshold is
reached, without waiting for context window overflow errors.

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/agents/conversation-management/
-------------------------------------------------------
"""


# --- 1. Conversation manager with proactive compression ---
compression_config: ProactiveCompressionConfig = {
    "compression_threshold": 0.7,  # Compress when 70% of context window used
}

conversation_manager = SummarizingConversationManager(
    summary_ratio=0.3,  # Summarize to 30% of original content
    preserve_recent_messages=4,  # Always keep last 4 messages intact
    proactive_compression=compression_config,
)

print("=== Proactive Context Compression ===")
print(f"  compression_threshold: {compression_config['compression_threshold']}")
print(f"  summary_ratio: {conversation_manager.summary_ratio}")
print(f"  preserve_recent_messages: {conversation_manager.preserve_recent_messages}")
print()

# --- 2. Create agent with compression-enabled conversation manager ---
openai_model = OpenAIModel(
    client_args={
        "api_key": settings.OPENAI_API_KEY.get_secret_value()
        if settings.OPENAI_API_KEY
        else ""
    },
    model_id=settings.OPENAI_MODEL_NAME,
)

agent = Agent(
    model=openai_model,
    system_prompt="You are a helpful assistant. Be concise.",
    conversation_manager=conversation_manager,
    callback_handler=null_callback_handler,
)

# --- 3. Simulate a multi-turn conversation ---
questions = [
    "What is the capital of Portugal?",
    "What is its population?",
    "What language do they speak there?",
    "What's the weather like in summer?",
]

print("=== Multi-Turn Conversation ===")
print()

for q in questions:
    print(f"Q: {q}")
    response = agent(q)
    print(f"A: {response}")
    print()

# --- 4. Show conversation state ---
messages = agent.messages
print(f"=== Conversation State ===")
print(f"  Total messages in context: {len(messages)}")
print(f"  (Proactive compression keeps context manageable across long conversations)")
