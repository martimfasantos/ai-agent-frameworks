from dotenv import load_dotenv

from deepagents import RubricMiddleware, create_deep_agent

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Deep Agents with the following features:
- RubricMiddleware: self-evaluated iteration against a quality rubric
- A grader sub-agent that revises the answer until it passes
- Observing each grading iteration via the on_evaluation callback

Sometimes "done" means meeting explicit quality criteria, not just
producing any answer. RubricMiddleware runs a separate grader sub-agent
each time the agent would finish: if the output fails the rubric, the
grader's feedback is fed back and the agent tries again (up to
max_iterations). Here we demand a specific format — a three-item numbered
list ending with a STATUS line — and watch the agent iterate until the
grader is satisfied.

For more details, visit:
https://docs.langchain.com/oss/python/deepagents/rubric
-----------------------------------------------------------------------
"""

# --- 1. Collect grading iterations as they happen ---
iterations = []


def on_evaluation(evaluation) -> None:
    iterations.append(evaluation)
    print(
        f"  [grader] iteration {evaluation['iteration']}: "
        f"result={evaluation['result']}"
    )


# --- 2. Add the rubric middleware (grader sub-agent + revision loop) ---
rubric_middleware = RubricMiddleware(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    on_evaluation=on_evaluation,
    max_iterations=3,
)
agent = create_deep_agent(
    model=f"openai:{settings.OPENAI_MODEL_NAME}",
    middleware=[rubric_middleware],
    system_prompt="You are a helpful assistant.",
)

# --- 3. Pass the rubric on the invocation state (activates the middleware) ---
rubric = (
    'The response MUST end with the exact line "STATUS: COMPLETE". '
    "The response MUST contain a numbered list of exactly three benefits."
)

print("=== Deep Agents Rubric Middleware ===")
print("Rubric: exactly 3 numbered benefits + a final 'STATUS: COMPLETE' line\n")
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "List benefits of unit testing."}],
        "rubric": rubric,
    }
)

# --- 4. Show the iterations and the final, rubric-satisfying answer ---
print(f"\nGrading iterations: {len(iterations)}")
print(f"\nFinal answer (passed the rubric):\n{result['messages'][-1].text}")
