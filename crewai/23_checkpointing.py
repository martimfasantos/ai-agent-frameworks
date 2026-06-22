import glob
import os
import shutil

from crewai import Agent, Task, Crew, CheckpointConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI with the following features:
- Checkpointing: automatically saving execution state during a run
- Resuming from a checkpoint after failure or interruption
- Forking from a checkpoint to explore alternative paths
- CheckpointConfig for custom checkpoint location and events
- Agent-level checkpoint with standalone kickoff

Checkpointing (new in v1.14.3+) lets crews, flows, and agents
save execution state after each completed task. If a run fails
mid-execution, you can resume from the last checkpoint without
re-running completed work. Forking creates a new execution branch
from any checkpoint, useful for "what if" exploration.

For more details, visit:
https://docs.crewai.com/en/concepts/checkpointing
-------------------------------------------------------
"""

CHECKPOINT_DIR = "./.checkpoints_demo"
AGENT_CP_DIR = "./.checkpoints_agent_demo"

# --- 1. Clean up any previous demo checkpoints ---
for d in [CHECKPOINT_DIR, AGENT_CP_DIR]:
    if os.path.exists(d):
        shutil.rmtree(d)

# --------------------------------------------------------------
# Example 1: Crew with checkpointing enabled
# --------------------------------------------------------------
print("=== Example 1: Crew with Checkpointing ===\n")

researcher = Agent(
    role="Researcher",
    goal="Research a given topic and provide key findings",
    backstory="You are an experienced researcher who distills complex topics into clear summaries.",
    llm=settings.OPENAI_MODEL_NAME,
)

writer = Agent(
    role="Writer",
    goal="Write a brief summary based on research findings",
    backstory="You are a concise technical writer.",
    llm=settings.OPENAI_MODEL_NAME,
)

research_task = Task(
    description="Research the topic: 'Benefits of checkpointing in AI agent systems'. Provide 3 key points.",
    expected_output="3 bullet points summarizing the benefits of checkpointing.",
    agent=researcher,
)

write_task = Task(
    description="Write a 2-sentence summary based on the research findings about checkpointing benefits.",
    expected_output="A concise 2-sentence summary.",
    agent=writer,
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    checkpoint=CheckpointConfig(
        location=CHECKPOINT_DIR,
        on_events=["task_completed", "crew_kickoff_completed"],
        max_checkpoints=5,
    ),
)

result = crew.kickoff()
print(f"\nCrew result: {result.raw[:300]}")

# --- 2. List saved checkpoints ---
checkpoint_files = sorted(glob.glob(os.path.join(CHECKPOINT_DIR, "**", "*.json"), recursive=True))
print(f"\nCheckpoints saved: {len(checkpoint_files)}")
for f in checkpoint_files:
    print(f"  - {os.path.basename(f)}")

# --------------------------------------------------------------
# Example 2: Agent-level checkpointing with standalone kickoff
# --------------------------------------------------------------
print("\n=== Example 2: Agent-Level Checkpointing ===\n")

standalone_agent = Agent(
    role="Quick Analyst",
    goal="Provide brief analysis on any topic",
    backstory="You are a fast, concise analyst. Respond in 1-2 sentences.",
    llm=settings.OPENAI_MODEL_NAME,
    checkpoint=CheckpointConfig(
        location=AGENT_CP_DIR,
        on_events=["lite_agent_execution_completed"],
    ),
)

agent_result = standalone_agent.kickoff("What are the main advantages of execution checkpointing?")
print(f"Agent result: {agent_result.raw[:300]}")

agent_cp_files = glob.glob(os.path.join(AGENT_CP_DIR, "**", "*.json"), recursive=True)
print(f"Agent checkpoints saved: {len(agent_cp_files)}")

# --------------------------------------------------------------
# Example 3: Forking from a checkpoint
# --------------------------------------------------------------
print("\n=== Example 3: Forking from a Checkpoint ===\n")

if checkpoint_files:
    fork_checkpoint = checkpoint_files[0]
    print(f"Forking from: {os.path.basename(fork_checkpoint)}")

    fork_config = CheckpointConfig(restore_from=fork_checkpoint)
    forked_crew = Crew.fork(fork_config, branch="experiment-alt")
    fork_result = forked_crew.kickoff(inputs={})
    print(f"Forked crew result: {fork_result.raw[:300]}")
else:
    print("No checkpoints available to fork from.")

# --- 4. Clean up demo checkpoints ---
for d in [CHECKPOINT_DIR, AGENT_CP_DIR]:
    if os.path.exists(d):
        shutil.rmtree(d)
print("\nDemo checkpoint directories cleaned up.")
