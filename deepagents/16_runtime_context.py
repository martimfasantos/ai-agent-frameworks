from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.tools import ToolRuntime

from deepagents import create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- Runtime context: immutable, per-invocation data passed at invoke time
- Declaring a context_schema on the agent
- Reading runtime context inside a tool via ToolRuntime

Runtime context is how you pass request-scoped data (the current user,
their permission tier, a tenant id) into an agent run without hard-coding
it into prompts or tools. You declare a context_schema, pass a context=
object to invoke(), and any tool can read it through a ToolRuntime
parameter. Here a whoami tool reports the identity supplied only at
invocation time — the same agent would answer differently for another
user with no code changes.

For more details, visit:
https://docs.langchain.com/oss/python/langchain/runtime
-----------------------------------------------------------------------
"""


# --- 1. Define the per-invocation context schema ---
@dataclass
class UserContext:
    user_name: str
    tier: str


# --- 2. A tool that reads the runtime context (not the prompt) ---
@tool
def whoami(runtime: ToolRuntime[UserContext]) -> str:
    """Return the current user's identity from runtime context."""
    ctx = runtime.context
    return f"user={ctx.user_name}, tier={ctx.tier}"


# --- 3. Register the context schema on the agent ---
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    tools=[whoami],
    context_schema=UserContext,
    system_prompt="Use the whoami tool to answer questions about the user.",
)

# --- 4. Invoke twice with different context — same agent, no code changes ---
print("=== Deep Agents Runtime Context ===")
for user in (UserContext("Marie", "gold"), UserContext("Tom", "free")):
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Who am I and what tier am I on? Use the tool."}]},
        context=user,
    )
    print(f"\ncontext={user}")
    print(f"Agent: {result['messages'][-1].text}")
