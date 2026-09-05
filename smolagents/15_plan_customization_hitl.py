from smolagents import AgentError, CodeAgent, OpenAIModel, PlanningStep, tool

from settings import settings

"""
-------------------------------------------------------
In this example, we explore smolagents human-in-the-loop plan customization:

- Dict-form `step_callbacks={PlanningStep: callback}` to target one step type
- Editing `step.plan` inside the callback so the agent follows the edit
- `agent.interrupt()` to stop a run mid-flight
- `agent.run(task, reset=False)` to resume with memory preserved

Every other example in this folder passes `step_callbacks` as a LIST, which
smolagents registers for `ActionStep` only. The DICT form registers per step
type, which is what makes it possible to hook the planning step specifically.
The callback runs before the plan is appended to memory, so mutating
`step.plan` changes the plan the agent actually executes. The reviewer's
decisions are hardcoded here so the example runs unattended; in a real app
that is where you would prompt a person.

For more details, visit:
https://huggingface.co/docs/smolagents/examples/plan_customization
-------------------------------------------------------
"""

# --- 1. Create the model ---
model = OpenAIModel(
    model_id=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
)


# --- 2. Define tools with a data dependency (region names are not known upfront) ---
@tool
def list_regions() -> str:
    """List the sales regions available in the reporting database.

    Returns:
        A comma-separated list of region identifiers.
    """
    return "north, south, east, west"


@tool
def get_region_revenue(region: str) -> str:
    """Get last-quarter revenue for one sales region.

    Args:
        region: A region identifier returned by list_regions.

    Returns:
        The revenue figure for that region, in EUR.
    """
    revenue = {"north": 1_200_000, "south": 890_000, "east": 1_450_000, "west": 610_000}
    if region.lower() not in revenue:
        return f"Unknown region '{region}'. Call list_regions first."
    return f"{region.lower()}: EUR {revenue[region.lower()]:,}"


# --- 3. The reviewer policy: inspect, edit, and pause the run once ---
REVIEWER_REQUIREMENT = "Name only the single top region and state its revenue in EUR."

reviewer = {"seen_plans": 0, "paused": False, "edited_plan": False}


def plan_steps_only(plan: str) -> str:
    """Drop the facts-survey preamble so only the numbered plan is reviewed."""
    _, marker, steps = plan.partition("## 2. Plan")
    return (marker + steps if marker else plan).strip().strip("`").strip()


def review_plan(step: PlanningStep, agent: CodeAgent) -> None:
    """Hook the planning step: show the plan, edit it, then interrupt the first run."""
    reviewer["seen_plans"] += 1

    print("\n" + "=" * 62)
    print(f"REVIEWER SEES PLAN #{reviewer['seen_plans']}")
    print("=" * 62)
    print(plan_steps_only(step.plan))
    print("=" * 62)

    if reviewer["paused"]:
        print("Reviewer decision: APPROVE -> letting the resumed run finish\n")
        return

    # In an interactive app, this is where input() would ask the human.
    step.plan = f"{step.plan.rstrip()}\n\nReviewer requirement: {REVIEWER_REQUIREMENT}"
    reviewer["edited_plan"] = True
    print(f"Reviewer decision: MODIFY  -> appended: {REVIEWER_REQUIREMENT}")
    print("Reviewer decision: PAUSE   -> agent.interrupt() called\n")
    reviewer["paused"] = True
    agent.interrupt()


# --- 4. Register the callback for PlanningStep only, via the dict form ---
agent = CodeAgent(
    tools=[list_regions, get_region_revenue],
    model=model,
    planning_interval=8,
    max_steps=8,
    step_callbacks={PlanningStep: review_plan},
    instructions=(
        "Make exactly one tool call per code block, print its result, and stop "
        "so you can observe it before deciding the next action."
    ),
)

TASK = "Which sales region had the highest revenue last quarter?"

print("=== Plan Customization (Human-in-the-Loop) Demo ===")
print("step_callbacks registered as a dict: {PlanningStep: review_plan}")

# --- 5. First run: the reviewer edits the plan, then interrupts the agent ---
print("\n--- Run 1 (reset=True, default): expected to be interrupted ---")
try:
    agent.run(TASK)
    print("Run 1 finished without an interrupt.")
except AgentError as error:
    print(f"Run 1 stopped by the reviewer: {error.message}")

steps_after_interrupt = len(agent.memory.steps)
print(f"\n--- Memory after the interrupt: {steps_after_interrupt} steps ---")
for i, step in enumerate(agent.memory.steps):
    print(f"  {i + 1}. {type(step).__name__}")

plan_in_memory = next(s for s in agent.memory.steps if isinstance(s, PlanningStep))
print(f"\nReviewer edit survived into memory: {REVIEWER_REQUIREMENT in plan_in_memory.plan}")

# --- 6. Resume with reset=False so the earlier steps are kept ---
print("\n--- Run 2 (reset=False): resume with memory preserved ---")
result = agent.run(TASK, reset=False)

print(f"\nFinal answer: {result}")
print("\n--- Summary ---")
print(f"Plans reviewed: {reviewer['seen_plans']} (edited: {reviewer['edited_plan']})")
print(f"Steps in memory: {steps_after_interrupt} after interrupt -> {len(agent.memory.steps)} after resume")
print(f"Memory preserved across the resume: {len(agent.memory.steps) > steps_after_interrupt}")
