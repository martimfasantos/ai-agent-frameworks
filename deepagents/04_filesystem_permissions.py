from dotenv import load_dotenv

from deepagents import create_deep_agent, FilesystemPermission
from deepagents.backends.utils import create_file_data

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Declarative filesystem permissions via the permissions= parameter
- Allow/deny rules evaluated in order with first-match-wins semantics
- Protecting sensitive paths from agent writes *and* deletions

Permissions let you control which files an agent may read or write. Each
rule declares operations ("read"/"write"), glob paths, and a mode
("allow"/"deny"). Rules are checked top to bottom and the first match
wins. Here we deny writes to anything named like a secret while allowing
everything else, then ask the agent to write both an allowed file and a
protected one so you can see the deny rule fire.

Since 0.7.0 the harness also exposes a recursive delete tool, classified
as a "write" operation. That cuts both ways: a broad write-allow rule
authorizes deleting the whole tree, and a write-deny rule is what stops
it. The second half of this example proves that on a /protected prefix.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/permissions
-----------------------------------------------------------------------
"""

# --- 1. Define permission rules (first match wins) ---
permissions = [
    # Deny writes to any file whose name starts with "secret" (paths are absolute)
    FilesystemPermission(operations=["write"], paths=["/**/secret*", "/secret*"], mode="deny"),
    # Deny writes under /protected — "write" covers delete too, so this blocks removal
    FilesystemPermission(operations=["write"], paths=["/protected/**"], mode="deny"),
    # Allow everything else
    FilesystemPermission(operations=["read", "write"], paths=["/**"], mode="allow"),
]

# --- 2. Create the agent with permissions ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    permissions=permissions,
    system_prompt=(
        "You are a filesystem assistant. Attempt every write the user asks for. "
        "If a write is blocked by permissions, note which file was blocked. "
        "Finish with a one-sentence summary of what succeeded and what was blocked."
    ),
)

# --- 3. Ask the agent to write an allowed and a protected file ---
print("=== Deep Agents Filesystem Permissions ===")
task = (
    "Write a file notes.txt containing 'hello', and also write a file secret.txt "
    "containing 'api-key-123'."
)
result = agent.invoke({"messages": [{"role": "user", "content": task}]})

# --- 4. Show which files actually made it into the filesystem ---
files = result.get("files", {})
print(f"\nFiles that were actually written: {list(files.keys())}")
print("(secret.txt should be missing — the deny rule blocked it)")

# --- 5. Print the agent's summary ---
print(f"\nAgent: {result['messages'][-1].text}")

# --- 6. The same rules gate the recursive delete tool ("write" operation) ---
seed_files = {
    "/draft.txt": create_file_data("scratch notes"),
    "/protected/config.txt": create_file_data("do not remove"),
}
delete_task = (
    "Delete /draft.txt and /protected/config.txt. Attempt both, then say in one "
    "sentence which deletion succeeded and which was blocked."
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": delete_task}], "files": seed_files}
)

print("\n=== Deletes are gated by the same write rules ===")
print(f"Seeded files: {sorted(seed_files)}")
print(f"Files remaining: {sorted(result.get('files', {}))}")
print("(/draft.txt was deleted; /protected/config.txt survived the write-deny rule)")
print(f"\nAgent: {result['messages'][-1].text}")
