from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_evals import Case, Dataset

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic Evals with the following features:
- Defining evaluation cases with inputs and expected outputs
- Creating datasets of test cases
- Running evaluate_sync to score agent responses
- Inspecting the EvaluationReport for pass/fail results

Pydantic Evals provides a structured way to test and evaluate AI agent
behavior. By defining cases with expected outputs, you can systematically
verify that your agents produce correct results and catch regressions
when models or prompts change.

For more details, visit:
https://pydantic.dev/docs/ai/evals/evals/
-----------------------------------------------------------------------
"""

# --- 1. Create the agent to evaluate ---
agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions=(
        "You are a geography expert. Answer questions about capital cities. "
        "Reply with ONLY the city name, nothing else."
    ),
)


# --- 2. Define a task function for evaluation ---
def ask_capital(question: str) -> str:
    """Run the agent and return its output."""
    result = agent.run_sync(question)
    return result.output.strip()


# --- 3. Create evaluation dataset ---
dataset = Dataset(
    name="Capital Cities Quiz",
    cases=[
        Case(
            name="france",
            inputs="What is the capital of France?",
            expected_output="Paris",
        ),
        Case(
            name="japan",
            inputs="What is the capital of Japan?",
            expected_output="Tokyo",
        ),
        Case(
            name="portugal",
            inputs="What is the capital of Portugal?",
            expected_output="Lisbon",
        ),
        Case(
            name="australia",
            inputs="What is the capital of Australia?",
            expected_output="Canberra",
        ),
    ],
)


# --- 4. Run evaluation ---
if __name__ == "__main__":
    print("=== Pydantic Evals: Capital Cities Quiz ===\n")

    report = dataset.evaluate_sync(ask_capital)

    # --- 5. Display results ---
    print(report)
