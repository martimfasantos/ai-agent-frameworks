from dotenv import load_dotenv
from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.eval.suite import Case, run_cases
from agno.models.openai import OpenAIChat
from agno.scorer import CodeScorer, ToolCallScorer
from agno.tools import tool

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Agno with the following features:
- agno.eval.suite.Case to declare eval cases and run_cases() to execute them
- CodeScorer to grade a typed answer against an expected value in plain Python
- ToolCallScorer to assert which tools actually executed, and with which arguments
- SuiteResult.to_dict() as the machine-readable payload a CI gate consumes

An eval suite turns "the agent seems fine" into a pass/fail gate. Both scorers
used here are deterministic and cost nothing beyond the agent's own run — no
judge model is involved — which makes the suite cheap enough to run on every
commit. Cases with `criteria=` instead grade with an LLM judge, at the price of
an extra model call per case.

For more details, visit:
https://docs.agno.com/evals/suite/overview
-------------------------------------------------------
"""

RATES = {"EUR": 1.09, "GBP": 1.27}


# --- 1. Define the tool and the output schema under test ---
@tool
def get_exchange_rate(currency: str) -> str:
    """Get the exchange rate of a currency against USD.

    Args:
        currency: The three-letter currency code, e.g. "EUR".

    Returns:
        How many USD one unit of that currency is worth.
    """
    rate = RATES.get(currency.upper())
    if rate is None:
        return f"No rate available for '{currency}'."
    return f"1 {currency.upper()} = {rate} USD"


class Conversion(BaseModel):
    currency: str = Field(description="The three-letter source currency code.")
    usd_amount: float = Field(description="The converted amount in USD.")


# --- 2. Create the agent under test ---
agent = Agent(
    name="currency-converter",
    model=OpenAIChat(id=settings.OPENAI_MODEL_NAME),
    tools=[get_exchange_rate],
    output_schema=Conversion,
    instructions=[
        "Always look up the exchange rate with the tool before converting.",
        "Never convert from memory.",
    ],
)


# --- 3. A deterministic scorer over the typed output ---
def usd_amount_matches(run, expected) -> bool:
    """Pass when the converted amount is within a cent of the expected value.

    `run.content` is the Conversion model, so the check compares a typed field
    rather than parsing prose.
    """
    return abs(run.content.usd_amount - expected) < 0.01


# --- 4. Declare the cases ---
cases = [
    Case(
        name="converts 100 EUR correctly",
        input="Convert 100 EUR to USD.",
        agent=agent,
        scorer=CodeScorer(usd_amount_matches),
        expected=109.0,
        tags=("currency",),
    ),
    Case(
        name="looks the rate up instead of guessing",
        input="Convert 50 GBP to USD.",
        agent=agent,
        scorer=ToolCallScorer(
            expected_tools=["get_exchange_rate"],
            arguments={"get_exchange_rate": {"currency": "GBP"}},
        ),
        tags=("currency", "reliability"),
    ),
]

# --- 5. Run the suite ---
print("=== Running eval suite ===\n")
suite_result = run_cases(cases)

# --- 6. Report ---
payload = suite_result.to_dict()
for case_payload in payload["cases"]:
    verdict = "PASS" if case_payload["passed"] else "FAIL"
    print(f"[{verdict}] {case_payload['name']}")
    print(f"  tags:         {', '.join(case_payload['tags'])}")
    print(f"  tools called: {case_payload['tools_called'] or 'none'}")
    print(f"  score:        {case_payload['score_value']} (passed={case_payload['score_passed']})")
    if case_payload["score_reason"]:
        print(f"  reason:       {case_payload['score_reason']}")
    print(f"  output:       {case_payload['output']}")
    print(f"  duration:     {case_payload['duration_seconds']:.2f}s")

summary = payload["summary"]
print(f"\nSuite: {summary['status']} — {summary['passed']}/{summary['total']} cases passed")

# --- 7. Fail the process on a red suite, the way a CI gate would ---
# cli() wraps this same runner with argument parsing and exit codes 0/1/2.
if summary["status"] != "PASS":
    raise SystemExit(1)
