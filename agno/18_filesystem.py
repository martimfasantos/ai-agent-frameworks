import os

from dotenv import load_dotenv

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.fs import FileSystem
from agno.models.openai import OpenAIChat
from agno.utils.pprint import pprint_run_response

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Agno with the following features:
- agno.fs.FileSystem — a durable, private file store for the agent
- fs.tools() to attach the file tools and fs.instructions() to compose their guidance
- A templated namespace ("notes/{user_id}") that isolates each user's files
- Programmatic access to the same store with fs.read() / fs.list() / fs.usage()

FileSystem is a third kind of agent state, orthogonal to the two already covered
here: 10_storage.py persists conversation transcripts, and 13_session_state.py
holds an ephemeral dict for the length of a session. FileSystem gives the agent
prose it writes for itself — notes that outlive any single session, stored in the
same SqliteDb and isolated per user by namespace.

For more details, visit:
https://docs.agno.com/filesystem/overview
-------------------------------------------------------
"""

DB_FILE = "/tmp/agno_filesystem_example.db"

# Start from a clean database so the example is reproducible.
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# --- 1. Back the file store with the same database as the sessions ---
db = SqliteDb(db_file=DB_FILE)

# "{user_id}" is resolved per tool call from the run context, never from a model
# argument, and fails closed when the run has no user_id.
fs = FileSystem(db, namespace="notes/{user_id}")

# --- 2. Attach the tools and compose the instructions ---
agent = Agent(
    model=OpenAIChat(id=settings.OPENAI_MODEL_NAME),
    db=db,
    tools=[fs.tools()],
    instructions=[
        "You are a research assistant who keeps durable notes about each user's project.",
        "Record lasting facts the user tells you in notes/project.md, and re-read your notes before answering.",
        "If your notes do not cover the question, say you have no note on it. Never guess.",
        "Keep replies to one or two sentences.",
        fs.instructions(),
    ],
    markdown=True,
)

# --- 3. Session 1: the agent writes a note ---
print("=== Session 1 (user: alice) — record a durable fact ===\n")
run_output = agent.run(
    "I'm benchmarking vector databases for a RAG pipeline. We settled on LanceDb "
    "because it runs embedded with no server. Note that down.",
    user_id="alice",
    session_id="alice-session-1",
)
pprint_run_response(run_output)

# --- 4. Session 2: a brand-new session with no conversation history ---
# Nothing carries over except the file store, so an answer here can only come
# from the note written above.
print("\n=== Session 2 (user: alice, new session) — recall from the file store ===\n")
run_output = agent.run(
    "Which vector database did we pick, and why?",
    user_id="alice",
    session_id="alice-session-2",
)
pprint_run_response(run_output)

# --- 5. A different user hits the same agent and the same database ---
print("\n=== Session 3 (user: bob) — namespace isolation ===\n")
run_output = agent.run(
    "Which vector database did we pick, and why?",
    user_id="bob",
    session_id="bob-session-1",
)
pprint_run_response(run_output)

# --- 6. Inspect the store programmatically ---
# resolve() binds the templated namespace outside of a run.
print("\n=== The store, seen from outside the agent ===\n")
for user_id in ("alice", "bob"):
    user_fs = fs.resolve(user_id=user_id)
    files = user_fs.list()
    usage = user_fs.usage()
    print(f"namespace 'notes/{user_id}': {usage.file_count} file(s), {usage.total_bytes} bytes")
    for meta in files:
        print(f"  - {meta.path} ({meta.size_bytes} bytes, version {meta.version})")

alice_note = fs.resolve(user_id="alice").read("notes/project.md")
print("\nContents of alice's notes/project.md:")
print(alice_note)
