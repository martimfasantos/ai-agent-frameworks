import logfire
from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import (
    ArgumentCorrectness,
    GEval,
    MaxModelRequests,
    MaxToolCalls,
    ToolCorrectness,
    TrajectoryMatch,
)

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic Evals with the following features:
- ToolCorrectness: did the agent call the tools it was supposed to?
- TrajectoryMatch: did it call them in the right order?
- ArgumentCorrectness: did a tool receive the arguments we expected?
- MaxToolCalls / MaxModelRequests: did it stay within budget?
- GEval: chain-of-thought LLM grading of the final answer

17_evals.py grades only the final output. Agentic evaluators grade HOW
the agent got there, by reading the OpenTelemetry span tree recorded
during the run. They are deterministic and never call an LLM, so they
are cheap enough to run on every case. GEval is the one exception: it
asks a model to reason through explicit evaluation steps before scoring.

NOTE: The span-based evaluators need logfire configured to capture spans.
`send_to_logfire=False` keeps everything local -- no account, no network.

For more details, visit:
https://pydantic.dev/docs/ai/evals/evaluators/agentic/
-----------------------------------------------------------------------
"""

# --- 1. Capture spans locally so the agentic evaluators can read them ---
logfire.configure(send_to_logfire=False, console=False)
logfire.instrument_pydantic_ai()


# --- 2. Build a small support agent with three tools ---
ORDERS = {
    "A-100": {"item": "keyboard", "status": "delivered"},
    "A-200": {"item": "monitor", "status": "lost in transit"},
}

agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions=(
        "You are a support agent. Always look the order up first. "
        "Only issue a refund for an order that was lost in transit. "
        "Answer in one short sentence."
    ),
)


@agent.tool_plain
def lookup_order(order_id: str) -> str:
    """Look up an order by its ID."""
    order = ORDERS.get(order_id)
    return f"{order['item']} - {order['status']}" if order else "No such order"


@agent.tool_plain
def issue_refund(order_id: str, reason: str) -> str:
    """Issue a refund for an order."""
    return f"Refund issued for {order_id} ({reason})"


def handle_ticket(ticket: str) -> str:
    """Task under evaluation: run the agent on one support ticket."""
    return agent.run_sync(ticket).output.strip()


# --- 3. Cases carry their own trajectory expectations ---
dataset = Dataset(
    name="Support Agent Trajectories",
    cases=[
        Case(
            name="lost_order_refunded",
            inputs="Order A-200 never arrived. Please sort it out.",
            evaluators=[
                # The multiset of tools that should have been called
                ToolCorrectness(expected_tools=["lookup_order", "issue_refund"]),
                # ...and the order they should have been called in
                TrajectoryMatch(
                    expected_trajectory=["lookup_order", "issue_refund"],
                    order="in_order",
                ),
                # The refund must be for the order the customer asked about
                ArgumentCorrectness(
                    tool_name="issue_refund",
                    expected_arguments={"order_id": "A-200"},
                ),
            ],
        ),
        Case(
            name="delivered_order_not_refunded",
            inputs="What happened to order A-100?",
            evaluators=[
                # A delivered order must NOT be refunded, so lookup alone
                ToolCorrectness(expected_tools=["lookup_order"]),
            ],
        ),
    ],
    evaluators=[
        # Budget checks applied to every case
        MaxToolCalls(max_calls=3),
        MaxModelRequests(max_requests=4),
        # Chain-of-thought grading of the final answer
        GEval(
            criteria="The reply resolves the customer's ticket accurately and politely.",
            evaluation_steps=[
                "Check the reply states the order's actual status.",
                "Check a refund is mentioned only if the order was lost in transit.",
                "Check the tone is courteous and the reply is a single sentence.",
            ],
            model=settings.OPENAI_MODEL_NAME,
        ),
    ],
)


# --- 4. Run the evaluation ---
if __name__ == "__main__":
    print("=== Agentic Evals: grading the agent's trajectory ===\n")

    report = dataset.evaluate_sync(handle_ticket)
    print(report)

    # --- 5. Spell out which check produced each assertion mark ---
    print("\n=== Per-case evaluator breakdown ===")
    for case in report.cases:
        print(f"\n{case.name}")
        print(f"  answer: {case.output}")
        for name, assertion in case.assertions.items():
            mark = "PASS" if assertion.value else "FAIL"
            print(f"  [{mark}] {name}: {assertion.reason}")
        for name, score in case.scores.items():
            print(f"  [score] {name}: {score.value}")
