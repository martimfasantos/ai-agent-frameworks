from dotenv import load_dotenv

from deepagents import create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- The built-in virtual filesystem tools (write_file, read_file, ls)
- The default in-memory StateBackend that stores files in agent state
- Reading generated files back from state after the run

Every deep agent comes with a virtual filesystem. By default it is backed
by an in-memory StateBackend, so the agent can create, read, and edit
files during a run without touching your real disk. This is useful for
context offloading: the agent can write intermediate results to files
instead of keeping everything in the conversation. Here we ask the agent
to write a file, then inspect the filesystem stored in state.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/backends
-----------------------------------------------------------------------
"""

# --- 1. Create the agent (filesystem tools are built in) ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    system_prompt=(
        "You are a helpful assistant with access to a virtual filesystem. "
        "Use write_file to save content when asked, then confirm in one sentence."
    ),
)

# --- 2. Ask the agent to create a file ---
print("=== Deep Agents Virtual Filesystem ===")
task = "Write a file named haiku.txt containing a short haiku about the ocean, then tell me you saved it."
result = agent.invoke({"messages": [{"role": "user", "content": task}]})

# --- 3. Read the files back from state ---
files = result.get("files", {})
print(f"\nFiles in the virtual filesystem: {list(files.keys())}")
for name, data in files.items():
    # StateBackend stores each file as a dict with a "content" field plus metadata
    content = data["content"] if isinstance(data, dict) else data
    print(f"\n--- {name} ---")
    print(content)

# --- 4. Print the agent's confirmation ---
print(f"\nAgent: {result['messages'][-1].text}")
