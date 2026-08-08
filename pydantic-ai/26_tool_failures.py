import asyncio

from dotenv import load_dotenv

from pydantic_ai import Agent, ModelRetry, RunContext, ToolFailed

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- ModelRetry: a recoverable failure the model should try again differently
- ToolFailed: a terminal failure the model must accept and work around
- The retry budget, and why ToolFailed deliberately does not consume it
- RunContext.is_tool_available to branch on what the model can currently call

Both exceptions surface a failed tool result to the model, but they mean
opposite things. ModelRetry prepends correction instructions and spends
one unit of the tool's retry budget, so it fits bad arguments the model
can fix. ToolFailed reports a definitive failure -- a missing record, an
unsupported operation -- with no correction hint and no budget spend, so
the model stops hammering a call that will never succeed.

NOTE: MCP toolsets expose the same choice through
MCPToolset(tool_error_behavior='retry' | 'error' | 'failed').

For more details, visit:
https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/
-----------------------------------------------------------------------
"""

# Simulated backing store
EMPLOYEES = {"E-1001": "Ana Ribeiro", "E-1002": "Tomás Silva"}

# Counts how often each tool actually ran, so the printed claims cannot drift
call_counts: dict[str, int] = {}


def record(tool_name: str, arg: str) -> None:
    call_counts[tool_name] = call_counts.get(tool_name, 0) + 1
    print(f"  [tool] {tool_name}({arg!r})")


async def main():

    # ------------------------------------------------------------------
    # Example 1: ModelRetry -- the model can fix its own arguments
    # ------------------------------------------------------------------
    print("=== Example 1: ModelRetry (recoverable) ===")

    retry_agent = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Look up employees with the tool. Be concise.",
    )

    @retry_agent.tool_plain
    def lookup_employee(employee_id: str) -> str:
        """Look up an employee by ID."""
        # The docstring deliberately omits the ID format, so the first call
        # arrives malformed and ModelRetry is what teaches the model the shape.
        record("lookup_employee", employee_id)
        if not employee_id.startswith("E-"):
            raise ModelRetry(
                f"'{employee_id}' is not a valid ID. IDs are the letter E, "
                "a hyphen, then four digits, e.g. 'E-1001'."
            )
        return EMPLOYEES.get(employee_id, "No such employee")

    result1 = await retry_agent.run("Who is employee 1001?")
    print(f"Response: {result1.output}")
    print(f"lookup_employee calls: {call_counts.get('lookup_employee', 0)}")
    print("(ModelRetry sent the model back to fix its own argument)\n")

    # ------------------------------------------------------------------
    # Example 2: ToolFailed -- terminal, so the model adapts instead
    # ------------------------------------------------------------------
    print("=== Example 2: ToolFailed (terminal) ===")

    failed_agent = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions=(
            "Look up employees with the tool. If a lookup fails permanently, "
            "say so plainly instead of trying again. Be concise."
        ),
    )

    @failed_agent.tool_plain
    def fetch_employee(employee_id: str) -> str:
        """Fetch an employee record by ID, e.g. 'E-1001'."""
        record("fetch_employee", employee_id)
        if employee_id not in EMPLOYEES:
            # Retrying cannot help: the record simply does not exist
            raise ToolFailed(f"Employee {employee_id} does not exist in the directory.")
        return EMPLOYEES[employee_id]

    result2 = await failed_agent.run("Fetch the record for employee E-9999.")
    print(f"Response: {result2.output}")
    print(f"fetch_employee calls: {call_counts.get('fetch_employee', 0)}")
    print("(ToolFailed is terminal, so the model did not call it again)\n")

    # ------------------------------------------------------------------
    # Example 3: RunContext.is_tool_available
    # ------------------------------------------------------------------
    print("=== Example 3: RunContext.is_tool_available ===")

    aware_agent = Agent(
        model=settings.OPENAI_MODEL_NAME,
        instructions="Answer the user's question using the tools. Be concise.",
    )

    @aware_agent.tool
    def payroll_report(ctx: RunContext, employee_id: str) -> str:
        """Produce a payroll report for an employee."""
        # Branch on what the run can actually call right now
        can_fetch = ctx.is_tool_available("fetch_salary")
        print(f"  [tool] payroll_report: is_tool_available('fetch_salary') -> {can_fetch}")
        if not can_fetch:
            raise ToolFailed(
                "Payroll reporting is unavailable: the salary lookup tool is not "
                "enabled for this run."
            )
        return "unreachable in this example"

    result3 = await aware_agent.run("Give me the payroll report for E-1001.")
    print(f"Response: {result3.output}")
    print("(The tool checked its own dependency before failing terminally)")


if __name__ == "__main__":
    asyncio.run(main())
