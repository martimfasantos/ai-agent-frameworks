import os
import tempfile

from dotenv import load_dotenv

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- FilesystemBackend: persist agent files to a real directory on disk
- virtual_mode: agent paths are scoped under a root directory
- Verifying agent output by reading the file back from the real disk

By default a Deep Agent uses an ephemeral, in-memory StateBackend. The
FilesystemBackend instead reads and writes real files under a root_dir,
so the agent's work survives the process and can be inspected with any
tool. Under virtual_mode an agent path like /notes.txt is mapped to
<root_dir>/notes.txt — the default since 0.7.0, passed explicitly below
to make the mapping obvious. Here the agent creates a file and we prove
it exists by opening it directly from the filesystem.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/backends
-----------------------------------------------------------------------
"""

# --- 1. Create a real working directory on disk ---
workspace = tempfile.mkdtemp(prefix="deepagents_fs_")

# --- 2. Back the agent with a FilesystemBackend rooted at that directory ---
# virtual_mode=True is the default since 0.7.0; stated here for clarity
backend = FilesystemBackend(root_dir=workspace, virtual_mode=True)
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    backend=backend,
    system_prompt="You are a file assistant. Create files exactly as asked.",
)

# --- 3. Ask the agent to create a file ---
print("=== Deep Agents Local Filesystem Backend ===")
print(f"Workspace on disk: {workspace}")
request = "Create a file named notes.txt containing exactly: Hello from disk"
result = agent.invoke({"messages": [{"role": "user", "content": request}]})
print(f"\nAgent: {result['messages'][-1].text}")

# --- 4. Prove it landed on the real disk by reading it back ourselves ---
print("\nReal files written to disk:")
for name in sorted(os.listdir(workspace)):
    path = os.path.join(workspace, name)
    with open(path) as fh:
        print(f"  {name} -> {fh.read()!r}")
