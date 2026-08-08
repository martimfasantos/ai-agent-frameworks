from strands import Agent, tool
from strands.models.openai import OpenAIModel
from strands.types.agent import Limits

from settings import settings

"""
-------------------------------------------------------
In this example, we explore Strands Agents SDK with the following features:
- Per-invocation budget caps with agent(..., limits={...}) (new in v1.42.0)
- The Limits TypedDict: turns, output_tokens, total_tokens
- The new stop reasons limit_turns, limit_total_tokens, limit_output_tokens
- Resuming the same agent after a cap fires

Limits bound a single invocation, not the agent's lifetime, so they act as a
runaway/cost guard around one request. Caps are checked at the top of each loop
iteration, which means pending tool calls always finish first and agent.messages
is left in a state you can invoke again.

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/agents/agent-loop/
-------------------------------------------------------
"""


# --- 1. A tool so the agent needs more than one turn ---
@tool
def city_population(city: str) -> str:
    """Look up the population of a city.

    Args:
        city: City name.
    """
    populations = {"Lisbon": "548,703", "Porto": "231,962", "Braga": "193,333"}
    return populations.get(city, "unknown")


openai_model = OpenAIModel(
    client_args={
        "api_key": settings.OPENAI_API_KEY.get_secret_value()
        if settings.OPENAI_API_KEY
        else ""
    },
    model_id=settings.OPENAI_MODEL_NAME,
)


def build_agent() -> Agent:
    """Create a fresh agent with the population tool."""
    return Agent(
        model=openai_model,
        system_prompt="You are a research assistant. Use the tool. Be concise.",
        tools=[city_population],
        callback_handler=None,
    )


def report(result) -> None:
    """Print the stop reason next to the tokens actually spent."""
    usage = result.metrics.latest_agent_invocation.usage
    print(f"  stop_reason: {result.stop_reason}")
    print(f"  turns used: {len(result.metrics.latest_agent_invocation.cycles)}")
    print(f"  tokens: total={usage['totalTokens']} output={usage['outputTokens']}")


print("=== Invocation Limits: Per-Request Budget Caps ===\n")

# --- 2. A generous budget: the invocation completes normally ---
print("--- Within budget ---")
generous: Limits = {"turns": 5, "output_tokens": 2000, "total_tokens": 10000}
agent = build_agent()
result = agent("What is the population of Lisbon?", limits=generous)
report(result)
print(f"  Agent: {result.message['content'][0]['text']}\n")

# --- 3. A turn cap that trips: one turn is not enough to answer ---
print("--- turns=1 (tool runs, but the agent cannot summarise) ---")
capped = build_agent()
result = capped("What is the population of Porto?", limits={"turns": 1})
report(result)
print("  No final answer was produced — the loop stopped at the cap.\n")

# --- 4. The same agent is still reinvokable after a cap fires ---
print("--- Resuming the capped agent without limits ---")
print(f"  messages carried over: {len(capped.messages)}")
result = capped("Continue and give me the answer.")
report(result)
print(f"  Agent: {result.message['content'][0]['text']}\n")

# --- 5. A token cap that trips ---
print("--- total_tokens=50 (tripped at the next turn boundary) ---")
result = build_agent()("What is the population of Braga?", limits={"total_tokens": 50})
report(result)
print()

# --- 6. Summary ---
print("--- Summary ---")
print("Limits keys: turns, output_tokens, total_tokens (all optional, positive ints)")
print("Stop reasons: limit_turns, limit_total_tokens, limit_output_tokens")
print("Precedence when several trip at once: turns > total_tokens > output_tokens")
print("Token caps are soft: one oversized response can overshoot, because caps are")
print("checked at turn boundaries rather than inside a model call.")
