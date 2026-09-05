from dotenv import load_dotenv

from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Long-term memory via the memory= parameter (AGENTS.md files)
- Loading persistent user preferences at agent startup
- Seeding memory files into the default StateBackend

Memory gives an agent persistent context that is always loaded, such as
user preferences, conventions, and project guidelines. You point the
memory= parameter at one or more AGENTS.md files; their content is
injected into the system prompt at startup so the agent "remembers" facts
without them being restated each turn. Here we preload a few facts about
the user and confirm the agent recalls them.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/customization#memory
-----------------------------------------------------------------------
"""

# --- 1. Author the memory file content (AGENTS.md format) ---
AGENTS_MD = """# Agent Memory

## About the user
- The user's name is Marie.
- Marie is a marine biologist based in Lisbon.
- Marie prefers concise answers and metric units.
"""

# --- 2. Create the agent, pointing memory at the AGENTS.md path ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    memory=["/memory/AGENTS.md"],
    system_prompt="You are a helpful personal assistant. Reply in one sentence.",
)

# --- 3. Seed the memory file into the virtual filesystem (StateBackend) ---
seed_files = {"/memory/AGENTS.md": create_file_data(AGENTS_MD)}

# --- 4. Ask something that requires the remembered context ---
print("=== Deep Agents Memory ===")
question = "Remind me — who am I and what do I do for work?"
result = agent.invoke(
    {"messages": [{"role": "user", "content": question}], "files": seed_files}
)

# --- 5. Print the answer, which draws on the loaded memory ---
print(f"\nLoaded memory from /memory/AGENTS.md")
print(f"User: {question}")
print(f"Agent: {result['messages'][-1].text}")
