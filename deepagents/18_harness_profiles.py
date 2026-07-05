from dotenv import load_dotenv

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
profile that forces every answer to start with "AHOY:" and removes the
write_todos tool, then confirm the house style takes effect.

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

# --- 3. Build an agent for that model — no per-call prompt tweaks needed ---
agent = create_deep_agent(
    model=model_key,
    system_prompt="You are a concise assistant.",
)

# --- 4. Ask a plain question; the profile reshapes the response ---
question = "What is 2 + 2? Answer briefly."
result = agent.invoke({"messages": [{"role": "user", "content": question}]})

print(f"\nUser: {question}")
print(f"Agent: {result['messages'][-1].text}")

# --- 5. The 'AHOY:' prefix proves the registered profile was applied ---
applied = result["messages"][-1].text.strip().startswith("AHOY:")
print(f"\nHouse-style profile applied (answer starts with 'AHOY:'): {applied}")
