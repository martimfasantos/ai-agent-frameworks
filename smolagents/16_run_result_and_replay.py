import json

from smolagents import CodeAgent, OpenAIModel, tool

from settings import settings

"""
-------------------------------------------------------
In this example, we explore smolagents run results and replay:

- `agent.run(..., return_full_result=True)` returning a `RunResult`
- `RunResult.output`, `.state`, `.steps`, `.token_usage`, `.timing`
- `RunResult.dict()` for a JSON-serializable run record
- `agent.replay()` to re-print every step of the last run
- `agent.visualize()` to draw the agent's tool/sub-agent tree

`12_callbacks_observability.py` builds the same kind of run report by hand: it
appends to a list from a step callback, counts the steps itself, and has no
token or timing data at all. `RunResult` carries all of it natively, so reach
for `return_full_result=True` when you want run metrics and for callbacks when
you need to react while the run is still going. (`RunResult.messages` is
deprecated since 1.22 — use `.steps`.)

For more details, visit:
https://huggingface.co/docs/smolagents/tutorials/memory
-------------------------------------------------------
"""

# --- 1. Create the model ---
model = OpenAIModel(
    model_id=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
)


# --- 2. Define a tool ---
@tool
def get_open_tickets(team: str) -> int:
    """Get the number of open support tickets for a team.

    Args:
        team: The team name (one of: billing, platform, mobile).

    Returns:
        The open ticket count for that team, or -1 if the team is unknown.
    """
    tickets = {"billing": 42, "platform": 17, "mobile": 8}
    return tickets.get(team.lower(), -1)


# --- 3. Create the agent (one tool call per step, so the run spans several steps) ---
agent = CodeAgent(
    tools=[get_open_tickets],
    model=model,
    max_steps=5,
    name="support_analyst",
    description="Answers questions about the support ticket backlog.",
    instructions=(
        "Make exactly one tool call per code block, print its result, and stop "
        "so you can observe it before deciding the next action."
    ),
)

# --- 4. Run and ask for the full result object instead of just the answer ---
print("=== RunResult & Replay Demo ===\n")

result = agent.run(
    "How many open tickets do the billing and mobile teams have in total? "
    "Answer in one short sentence.",
    return_full_result=True,
)

# --- 5. Read the RunResult fields ---
print(f"\n--- RunResult ({type(result).__name__}) ---")
print(f"  output : {result.output}")
print(f"  state  : {result.state}")
print(f"  steps  : {len(result.steps)} recorded")
print(f"  tokens : input={result.token_usage.input_tokens} "
      f"output={result.token_usage.output_tokens} "
      f"total={result.token_usage.total_tokens}")
print(f"  timing : {result.timing.duration:.2f}s "
      f"(start={result.timing.start_time:.0f}, end={result.timing.end_time:.0f})")

# --- 6. Per-step breakdown, straight from result.steps ---
print("\n--- Per-step breakdown (no hand-counting needed) ---")
for step in result.steps:
    if "step_number" not in step:
        print(f"  task step     : {step['task']}")
        continue
    tokens = step["token_usage"] or {}
    flags = [name for name, on in [("error", step["error"]), ("final answer", step["is_final_answer"])] if on]
    detail = f"{step['timing']['duration']:.2f}s, {tokens.get('total_tokens', 0)} tokens"
    print(f"  action step {step['step_number']} : {detail}" + (f" [{', '.join(flags)}]" if flags else ""))

# --- 7. RunResult.dict() gives a JSON-serializable run record ---
payload = result.dict()
print("\n--- RunResult.dict() ---")
print(f"  keys: {list(payload.keys())}")
print(f"  token_usage: {payload['token_usage']}")
print(f"  serialized size: {len(json.dumps(payload))} chars of JSON")
print("\nEverything above came from one RunResult; 12_callbacks_observability.py")
print("assembles a smaller version of it by hand from a step callback.")

# --- 8. Replay the whole run from memory ---
print("\n--- agent.replay(): every step re-printed from agent.memory ---")
print("(replay() dumps the full system prompt first, then each step's output)")
agent.replay()

# --- 9. Visualize the agent's tool tree ---
print("\n--- agent.visualize(): agent structure ---")
agent.visualize()
