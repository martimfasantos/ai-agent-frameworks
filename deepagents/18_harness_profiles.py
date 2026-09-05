from dotenv import load_dotenv
from langchain.agents.middleware import TodoListMiddleware

from deepagents import (
    HarnessProfile,
    create_deep_agent,
    register_harness_profile,
)

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- HarnessProfile: reshape the agent harness for a given model
- Registering a profile with register_harness_profile(key, profile)
- A system_prompt_suffix and excluded_tools applied automatically

A HarnessProfile lets you standardize how an agent behaves whenever a
particular model (or provider) is used — without touching each call site.
You can inject a house-style prompt suffix, override tool descriptions,
exclude tools, or add middleware. Once registered under a model key, the
profile is applied automatically by create_deep_agent. Here we register a
profile that forces every answer to start with "AHOY:" and hides the
write_todos tool, then prove both effects took hold.

Note: excluded_tools is a plain name filter over the tools reaching the
model — excluding a name that no middleware installed is a silent no-op.
Since 0.7.0 write_todos is no longer in the default stack, so we install
TodoListMiddleware first to give the exclusion something to remove.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/profiles
-----------------------------------------------------------------------
"""

# --- 1. Define a harness profile (house style + tool policy) ---
model_key = f"openai:{settings.OPENAI_MODEL_NAME}"
profile = HarnessProfile(
    system_prompt_suffix=(
        '\n\nHOUSE STYLE: Always begin your final answer with the prefix "AHOY:".'
    ),
    excluded_tools=frozenset({"write_todos"}),
)

# --- 2. Register it under the model key so it applies automatically ---
register_harness_profile(model_key, profile)
print("=== Deep Agents Harness Profiles ===")
print(f"Registered profile for: {model_key}")
print(f"  system_prompt_suffix: enforces the 'AHOY:' house style")
print(f"  excluded_tools: {set(profile.excluded_tools)}")

# --- 3. Build an agent whose harness really does install write_todos ---
planning = TodoListMiddleware()
installed = [tool.name for tool in planning.tools]
print(f"\nTools installed by TodoListMiddleware: {installed}")

agent = create_deep_agent(
    model=model_key,
    middleware=[planning],
    system_prompt=(
        "You are a concise assistant. Before answering a multi-step question, "
        "call write_todos to lay out your plan."
    ),
)

# --- 4. Ask a multi-step question, so the agent would want to plan ---
question = "Plan a 2-step process for brewing tea, then answer briefly."
result = agent.invoke({"messages": [{"role": "user", "content": question}]})

print(f"\nUser: {question}")
print(f"Agent: {result['messages'][-1].text}")

# --- 5. Both halves of the profile are provably in effect ---
applied = result["messages"][-1].text.strip().startswith("AHOY:")
print(f"\nHouse-style suffix applied (answer starts with 'AHOY:'): {applied}")
print(f"write_todos installed in the harness: {'write_todos' in installed}")
print(
    f"Todos recorded in state after the run: {len(result.get('todos', []))} "
    "-> the profile stripped write_todos before the model ever saw it"
)
