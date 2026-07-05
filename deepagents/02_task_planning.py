from dotenv import load_dotenv

from deepagents import create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- The built-in write_todos task-planning tool
- Reading the agent's plan back from state after the run
- How the harness tracks pending / in_progress / completed tasks

Deep Agents ship with a write_todos tool out of the box. For multi-step
work, the agent maintains a structured task list in its state so it can
plan, track progress, and stay organized on long-running tasks. Here we
give the agent a small multi-step task and then print the todo list it
built to organize the work.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/overview#task-planning
-----------------------------------------------------------------------
"""

# --- 1. Create the agent (write_todos is built in) ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    system_prompt=(
        "You are a project planner. For any multi-step task, first use the "
        "write_todos tool to lay out the plan, then give a one-sentence summary."
    ),
)

# --- 2. Invoke with a multi-step task ---
print("=== Deep Agents Task Planning ===")
task = "Plan a 3-step process for launching a simple blog: pick a platform, write a first post, and publish it."
result = agent.invoke({"messages": [{"role": "user", "content": task}]})

# --- 3. Inspect the plan the agent stored in state ---
todos = result.get("todos", [])
print(f"\nTask: {task}\n")
print(f"Agent created {len(todos)} todo(s):")
for i, todo in enumerate(todos, start=1):
    print(f"  {i}. [{todo['status']}] {todo['content']}")

# --- 4. Print the agent's summary ---
print(f"\nSummary: {result['messages'][-1].text}")
