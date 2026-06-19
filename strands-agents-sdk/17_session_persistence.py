import json
import tempfile

from strands import Agent
from strands.models.openai import OpenAIModel
from strands.session.file_session_manager import FileSessionManager

from settings import settings

"""
-------------------------------------------------------
In this example, we explore Strands Agents SDK with the following features:
- Session persistence with FileSessionManager
- Saving and restoring agent state and conversation history
- Resuming conversations across agent instances
- Agent state (key-value storage) persisted alongside messages

Session management lets agents maintain context across restarts.
Strands provides FileSessionManager (local filesystem) and
S3SessionManager (cloud) as built-in backends.

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/agents/session-management/
-------------------------------------------------------
"""

# --- 1. Configure model ---
openai_model = OpenAIModel(
    client_args={
        "api_key": settings.OPENAI_API_KEY.get_secret_value()
        if settings.OPENAI_API_KEY
        else ""
    },
    model_id=settings.OPENAI_MODEL_NAME,
)

# --- 2. Create a session manager with a temporary directory ---
session_dir = tempfile.mkdtemp(prefix="strands_session_")
session_id = "demo-session-001"

print("=== Session Persistence with FileSessionManager ===\n")
print(f"Session directory: {session_dir}")
print(f"Session ID: {session_id}\n")

# --- 3. First agent instance — start a conversation ---
print("--- First Agent Instance ---")
session_manager_1 = FileSessionManager(
    session_id=session_id,
    storage_dir=session_dir,
)
agent_1 = Agent(
    model=openai_model,
    system_prompt="You are a helpful assistant. Keep responses to 1-2 sentences.",
    session_manager=session_manager_1,
    callback_handler=None,
)

# Set some agent state
agent_1.state.set("user_name", "Alice")
agent_1.state.set("interaction_count", 1)

result_1 = agent_1("My favorite color is blue. Remember that.")
print(f"Agent: {result_1.message['content'][0]['text']}")
print(f"Messages in history: {len(agent_1.messages)}")
print(f"Agent state: user_name={agent_1.state.get('user_name')}, "
      f"interaction_count={agent_1.state.get('interaction_count')}")

# --- 4. Second agent instance — resume the conversation ---
print("\n--- Second Agent Instance (Resumed) ---")
session_manager_2 = FileSessionManager(
    session_id=session_id,  # Same session ID to restore
    storage_dir=session_dir,
)
agent_2 = Agent(
    model=openai_model,
    system_prompt="You are a helpful assistant. Keep responses to 1-2 sentences.",
    session_manager=session_manager_2,
    callback_handler=None,
)

# Verify state was restored
print(f"Restored messages: {len(agent_2.messages)}")
print(f"Restored state: user_name={agent_2.state.get('user_name')}, "
      f"interaction_count={agent_2.state.get('interaction_count')}")

# Continue the conversation — the agent should remember the favorite color
agent_2.state.set("interaction_count", 2)
result_2 = agent_2("What is my favorite color?")
print(f"Agent: {result_2.message['content'][0]['text']}")
print(f"Total messages now: {len(agent_2.messages)}")

# --- 5. Summary ---
print("\n--- Summary ---")
print("Session persistence preserves:")
print("  - Conversation history (messages)")
print("  - Agent state (key-value storage)")
print("  - Conversation manager state")
print("Built-in backends: FileSessionManager, S3SessionManager")
