from dotenv import load_dotenv

from deepagents import create_deep_agent, SubAgent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Defining custom subagents with the SubAgent spec
- Delegating isolated subtasks via the built-in task tool
- Giving a subagent its own tools and system prompt

Deep Agents can spawn ephemeral subagents to handle isolated, focused
subtasks in a fresh context window. The main agent delegates through the
built-in "task" tool, the subagent runs autonomously to completion, and
it returns a single compact report. This keeps heavy subtask work out of
the main agent's context. Here we define a specialized "math-expert"
subagent and let the main agent delegate a calculation to it.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/subagents
-----------------------------------------------------------------------
"""


# --- 1. Define a tool the subagent will use ---
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the product."""
    print(f"[subagent tool] multiply({a}, {b})")
    return a * b


# --- 2. Define a custom subagent ---
math_expert: SubAgent = {
    "name": "math-expert",
    "description": "Handles precise arithmetic. Delegate any calculation to this subagent.",
    "system_prompt": "You are a math expert. Use the multiply tool for products and report the result.",
    "tools": [multiply],
}

# --- 3. Create the main agent with the subagent ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    subagents=[math_expert],
    system_prompt=(
        "You are a coordinator. Delegate any math to the math-expert subagent "
        "using the task tool. Give the final answer in one sentence."
    ),
)

# --- 4. Invoke a task that triggers delegation ---
print("=== Deep Agents Subagents ===")
question = "A warehouse has 23 shelves with 17 boxes each. Delegate the math and tell me the total number of boxes."
result = agent.invoke({"messages": [{"role": "user", "content": question}]})

# --- 5. Show that the task tool was used to delegate ---
tool_calls_used = [
    tc["name"]
    for msg in result["messages"]
    for tc in (getattr(msg, "tool_calls", None) or [])
]
print(f"\nTools the main agent called: {tool_calls_used}")
print("(the 'task' tool means work was delegated to a subagent)")

# --- 6. Print the final answer ---
print(f"\nAgent: {result['messages'][-1].text}")
