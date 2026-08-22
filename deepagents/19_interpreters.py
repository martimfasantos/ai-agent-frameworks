from dotenv import load_dotenv
from langchain_quickjs import CodeInterpreterMiddleware

from deepagents import create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Code interpreters: let the agent execute real code, not just guess
- The QuickJS CodeInterpreterMiddleware (a sandboxed JS eval tool)
- Grounding numeric answers in actual computation

LLMs are unreliable at arithmetic and multi-step computation. A code
interpreter gives the agent a sandboxed runtime it can call to compute
exact results. The QuickJS middleware exposes an eval tool that runs
JavaScript in an isolated engine and returns the real output. Here we ask
for a sum of squares — the agent writes JS, runs it, and reports the
computed value (2870) instead of estimating.

Install with: uv add "deepagents[quickjs]"

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/interpreters
-----------------------------------------------------------------------
"""

# --- 1. Add the sandboxed JavaScript interpreter as an eval tool ---
interpreter = CodeInterpreterMiddleware(tool_name="eval")
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    middleware=[interpreter],
    system_prompt=(
        "You can run JavaScript with the eval tool. "
        "Use it for any calculation instead of computing in your head."
    ),
)

# --- 2. Ask for something the agent should compute, not guess ---
print("=== Deep Agents Interpreters ===")
question = "Using the eval tool, compute the sum of squares from 1 to 20. Show the number."
result = agent.invoke({"messages": [{"role": "user", "content": question}]})

# --- 3. Show the code the agent ran and the sandbox's real output ---
for msg in result["messages"]:
    if msg.type == "ai" and msg.tool_calls:
        for tc in msg.tool_calls:
            if tc["name"] == "eval":
                print(f"\n[agent ran JS]\n{tc['args'].get('code')}")
    if msg.type == "tool":
        print(f"\n[sandbox output] {msg.text}")

print(f"\nUser: {question}")
print(f"Agent: {result['messages'][-1].text}")
